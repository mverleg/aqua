
import random
import time
import datetime
from django.core.management.base import BaseCommand
from math import sqrt
from timeslot.models import Roster, TimeSlot, RosterWorker
from distribute.models import Availability, Assignment
from aqua.functions.to_hours import to_hours
from aqua.functions.week_start_date import week_start_date
from optparse import make_option
from django.contrib.auth import get_user_model


class Command(BaseCommand):
	option_list = BaseCommand.option_list + (
		make_option('-c', '--check', action = 'store_true', dest = 'check', default = False, help = 'Check consistency of the distribution (for debugging)'),
		make_option('-f', '--force', action = 'store_true', dest = 'force', default = False, help = 'Force recalculation of an already distributed roster'),
		make_option('-s', '--steps', action = 'store', dest = 'steps', default = 2000, type = 'int', help = 'How many steps without change before quitting'),
		make_option('-a', '--alpha', action = 'store', dest = 'alpha', default = 18, type = 'float', help = 'How much are flexible people rewarded?'),
	)
	help = 'Distribute a schedule [pk = arg0].'

	def handle(self, *args, **options):

		""" Input arguments """
		t_init = time.time()
		try:
			roster = Roster.objects.get(pk = int(args[0]))
		except IndexError:
			print 'Please provide a roster ID'
			show_rosters()
			return
		except ValueError:
			print 'Please provide an integer roster ID\n'
			show_rosters()
			return
		except Roster.DoesNotExist:
			print 'Roster with ID %s not found\n' % args[0]
			show_rosters()
			return

		N = options['steps']
		check_consistency = options['check']
		alpha = options['alpha']

		if roster.state < 1:
			print 'This roster is is not ready to distribute yet, complete other steps first'
			return
		elif roster.state == 3:
			if options['force']:
				roster.state = 2
				roster.save()
			else:
				print 'This roster has already been distributed; use -f to force redistribution'
				return
		elif roster.state > 3:
			print 'This roster has already been distributed'
			return
		elif roster.state == 1:
			roster.state = 2
			roster.save()

		print '* %s *' % roster.name.upper()

		''' Create the availability data structure '''
		t_load = time.time()
		slotmap = {ts.pk: ts for ts in TimeSlot.objects.filter(roster = roster)}
		availabilities_qs = Availability.objects.filter(timeslot__roster = roster)
		t_assign = time.time()
		print 'TIME query data:   %.3fs' % (t_assign - t_load)

		A, D = {}, {}
		degeneracy, duration, similar = {}, {}, {}
		slots = []
		total_hours = 0
		for slot in slotmap.values():
			slots.append(slot)
			D[slot.pk] = slot.degeneracy * [None]
			A[slot.pk] = []
			degeneracy[slot.pk] = slot.degeneracy
			duration[slot.pk] = to_hours(slot.duration)
			similar[slot.pk] = []
			total_hours += slot.degeneracy * to_hours(slot.duration)
			''' Find similar shifts (exactly a week difference) '''
			monday = week_start_date(slot.start.isocalendar()[0], slot.start.isocalendar()[1])
			day = datetime.timedelta(days = 1)
			weeks = 0 * day
			while monday + weeks >= datetime.datetime.combine(roster.start, datetime.time()):
				weeks -= 7 * day
			while monday + weeks <= datetime.datetime.combine(roster.end, datetime.time()):
				if not ((monday + weeks).isocalendar()[0] == slot.start.isocalendar()[0] and (monday + weeks).isocalendar()[1] == slot.start.isocalendar()[1]):
					sim_slot = TimeSlot.objects.filter(roster = roster).filter(roster = slot.roster, start = slot.start + weeks, end = slot.end + weeks)
					if sim_slot:
						similar[slot.pk].append(sim_slot[0])
				weeks += 7 * day

		for availability in availabilities_qs:
			''' There should be no duplicates but it happens, somehow. Don't know where
				they come from, but I can't block them at database level because sqlite
				seems to throw random errors for unique_together... '''
			if availability.user.pk not in map_user_pk(A[availability.timeslot.pk]):
				A[availability.timeslot.pk].append(availability)
			else:
				print 'There was a duplicate Availability; #%d removed' % availability.pk
				Availability.objects.get(pk = availability.pk).delete()

		if not N:
			N = 10 * len(slots)

		''' Calculate the hours '''
		"""
			extra hours for flexibility are calculated as:
			alpha * sqrt(user_available_hours / per_person_expected)
			[but never negative]
		"""
		t_hours = time.time()
		print 'TIME assign data:  %.3fs' % (t_hours - t_assign)
		workers = RosterWorker.objects.filter(roster = roster)
		current_hours = {}
		extra_hours = {}
		flexibility = {}
		expected_hours = float(total_hours) / len(workers)
		available_hours = {worker.user.pk: 0 for worker in workers}
		for availability_list in A.values():
			for availability in availability_list:
				available_hours[availability.user.pk] += to_hours(availability.timeslot.duration)
		for worker in workers:
			extra_hours[worker.user.pk] = worker.extra
			flexibility[worker.user.pk] = sqrt(available_hours[worker.user.pk] / expected_hours)
			extra_hours[worker.user.pk] += alpha * flexibility[worker.user.pk]
			current_hours[worker.user.pk] = 0

		''' Monte Carlo (with only favourable steps though) '''
		t_monte = time.time()
		no_change_steps = 0
		counter = 500 * len(slots)
		while no_change_steps < N and counter> 0:
			updated = False
			counter -= 1
			''' Trivial slots are removed; if there are no slots left we quit  '''
			if not len(slots):
				print 'DETERMINISTIC / TRIVIAL'
				break

			slot = weighted_choice(slots, degeneracy.values())
			if len(A[slot.pk]) <= degeneracy[slot.pk]:
				''' No competition for this position '''
				for deg in range(degeneracy[slot.pk]):
					min_av = select_fewest_hours(set(A[slot.pk]) - set(D[slot.pk]), current_hours, extra_hours)
					''' Note that one of the positions might have been filled through the recursion mechanism '''
					if min_av and not D[slot.pk][deg]:
						(D, current_hours, updated) = assign(min_av, A, D, slot, deg, current_hours)
				slots.remove(slot)
				degeneracy.pop(slot.pk)
			else:
				deg = random.randint(0, len(D[slot.pk]) - 1)
				if D[slot.pk][deg] == None:
					''' No current worker, so no comparison '''
					worker = random.choice(A[slot.pk])
					(D, current_hours, updated) = assign(worker, A, D, slot, deg, current_hours)
				elif len(A[slot.pk]) > 1:
					''' There is a selected worker, and at least one alternative '''
					worker = random.choice(A[slot.pk])
					while worker.pk == D[slot.pk][deg].pk:
						worker = random.choice(A[slot.pk])
					(D, current_hours, updated) = switch(slot, deg, worker, A, D, duration, similar, current_hours, extra_hours, recursive = True)

			''' Count the steps without change (the while loop quits after N of them)
				The only way assign is called multiple times is when there is one succesful
				switch, in which case True is returned anyway '''
			no_change_steps += 1
			if updated:
				no_change_steps = 0

		''' Prevent unnecessary blanks (generally none are found) '''
		t_post = time.time()
		print 'TIME monte carlo:  %.3fs' % (t_post - t_monte)
		for slot in slots:
			for deg in range(degeneracy[slot.pk]):
				if D[slot.pk][deg] == None:
					''' There is an empty slot; find the candidate with fewest hours '''
					min_av = select_fewest_hours(set(A[slot.pk]) - set(D[slot.pk]), current_hours, extra_hours)
					if min_av:
						(D, current_hours, updated) = assign(min_av, A, D, slot, deg, current_hours)

		''' Consistency checks '''
		t_check = time.time()
		print 'TIME post check:   %.3fs' % (t_check - t_post)
		if check_consistency:
			all_slot_check = 0
			for slot in slots:
				all_slot_check += to_hours(slot.duration) * slot.degeneracy
				''' Check the degeneracy values '''
				assert len(D[slot.pk]) == slot.degeneracy
				''' Check that there aren't more shifts occupied than there are available people '''
				assert len(filter(lambda x: x, D[slot.pk])) <= len(A[slot.pk])
				''' Check that a person doesn't have two shifts in one slot '''
				assert len(map_user_pk(D[slot.pk])) == len(set(map_user_pk(D[slot.pk])))
			''' Check that the total hours of all slots does not exceed the assigned hours '''
			all_assign_check = 0
			for slot_pk, avity_list in D.items():
				for deg, avity in enumerate(avity_list):
					if avity:
						all_assign_check += to_hours(avity.timeslot.duration)
						''' Check that all assigned shifts belong to someone that is available '''
						assert avity.pk in map_pk(A[slot_pk])
					else:
						''' If the slot is empty, then no one is available that isn't already working '''
						if len(set(map_pk(A[slot_pk])) - set(map_pk(D[slot_pk]))):
							print '>> %s | %s  (%d)' % (set(map_pk(A[slot_pk])), set(map_pk(D[slot_pk])), len(D[slot_pk]))
							print map_user_pk(A[slot_pk])
						assert len(set(map_pk(A[slot_pk])) - set(map_pk(D[slot_pk]))) == 0
			''' check sum of hours (bugged end 2013) and empty slots '''
			current_hours_check = {}
			for rw in workers:
				current_hours_check[rw.user.pk] = 0
			for slot_pk, avity_list in D.items():
				for deg, avity in enumerate(avity_list):
					if avity is None:
						''' check that, for every empty slot, there are fewer availabilities than places '''
						assert len(A[slot_pk]) <= [slot.degeneracy for slot in slotmap.values() if slot.pk == slot_pk][0]
					else:
						current_hours_check[avity.user.pk] += to_hours(avity.timeslot.duration)
			''' check that the total hours are the same '''
			assert sum(current_hours.values()) == sum(current_hours_check.values())
			assert len(current_hours) == len(current_hours_check)
			''' check that the hours for individual users are the same '''
			for user_pk in current_hours.keys():
				assert current_hours[user_pk] == current_hours_check[user_pk]

			''' Check that the hours of assigned shifts match the total of current_hours '''
			assert all_assign_check == sum(current_hours.values())

		''' Store result '''
		t_store = time.time()
		if check_consistency:
			print 'TIME checks:       %.3fs' % (t_store - t_check)
		else:
			print 'TIME checks:       off'
		roster = Roster.objects.get(pk = roster.pk)
		if not roster.state == 2:
			print 'The state of the roster has changed! There may be a concurrent process. Mission aborted; no changes will be made.'
			return
		Assignment.objects.filter(timeslot__in = slotmap.values()).delete()
		batch = []
		empty_slots = []
		for key, availability_list in D.items():
			for deg, availability in enumerate(availability_list):
				if availability is None:
					empty_slots.append(slotmap[key])
				else:
					batch.append(Assignment(user = availability.user, timeslot = availability.timeslot, note = 'shift %d' % deg))
		Assignment.objects.bulk_create(batch)
		roster.state = 3
		roster.save()

		''' Process the result '''
		t_result = time.time()
		print 'TIME store result: %.3fs' % (t_result - t_store)
		print 'TIME other steps:  %.3fs' % (t_result - t_init - (t_check - t_monte) - (t_hours - t_assign) - (t_assign - t_load) - (t_result - t_store) - (t_store - t_check))
		print 'TIME total time:   %.3fs' % (t_result - t_init)
		print 'remaining hours:   %d' % (total_hours - sum(current_hours.values()))
		for empty_slot in empty_slots:
			print '\t %s (%.1fh)' % (empty_slot, to_hours(empty_slot.duration))
		print 'with alpha = %.3f max extra hours is %.1fh' % (alpha, alpha * (max(flexibility.values()) - min(flexibility.values())))
		print '       user\tfinal\textra (goal)'
		for user_pk in current_hours.keys():
			print ' %-20s\t%d\t%.1f' % (unicode(get_user_model().objects.get(pk = user_pk))[:20], int(current_hours[user_pk]), extra_hours[user_pk])
		if not counter:
			print '(Monte Carlo reached iteration limit)'


''' Helper functions because this happens too much '''
def map_pk(items):
	return map(lambda item: item.pk, filter(lambda item: item, items))


def map_user_pk(items):
	return map(lambda item: item.user.pk, filter(lambda item: item, items))


''' Calculate whether it is advantageous to switch two availabilities
	Recursively checks similar shifts for possible switches '''
def switch(slot, deg, worker, A, D, duration, similar, current_hours, extra_hours, recursive = False):
	''' There is a selected worker, and at least one alternative '''
	slot_duration = duration[slot.pk]
	cost_old = hour_cost(current_hours, extra_hours, slot)
	if len(D[slot.pk]) > deg:
		if D[slot.pk][deg] == None:
			''' There is a free position for this shift (the day may be trivial but that's not a problem anymore) '''
			(D, current_hours, updated) = assign(worker, A, D, slot, deg, current_hours)
		else:
			''' be careful to store D[slot.pk][deg], because assign() can change it's value,
				which will make switching hours back not work, costing about 4 hours of debugging '''
			old_user_pk = D[slot.pk][deg].user.pk
			current_hours[old_user_pk] -= slot_duration
			current_hours[worker.user.pk] += slot_duration
			cost_new = hour_cost(current_hours, extra_hours, slot)
			if cost_new < cost_old:
				''' Let's change it (time was already updated) '''
				(D, current_hours, updated) = assign(worker, A, D, slot, deg, current_hours)
				if recursive:
					for try_slot in similar[slot.pk]:
						(D, current_hours) = switch(try_slot, deg, worker, A, D, duration, similar, current_hours, extra_hours, recursive = False)[0:2]
			else:
				updated = False
			current_hours[old_user_pk] += slot_duration
			current_hours[worker.user.pk] -= slot_duration
	else:
		updated = False

	return (D, current_hours, updated)


''' Select the availability with the fewest hours '''
def select_fewest_hours(available_set, current_hours, extra_hours):
	if len(available_set):
		min_worker = available_set.pop()
		min_hours = current_hours[min_worker.user.pk] - extra_hours[min_worker.user.pk]
		for available_worker in available_set:
			user_hours = current_hours[available_worker.user.pk] - extra_hours[available_worker.user.pk]
			if user_hours < min_hours:
				min_worker = available_worker
				min_hours = user_hours#current_hours[available_worker.user.pk] - extra_hours[available_worker.user.pk]
		return min_worker
	return None


''' Cost function, based on the hour distribution and on the time '''
''' Some shifts will be more expansive / cheaper than others, based on the time. '''
''' CAUTION: Multiplier currently only effective for shifts that have competition! '''
def hour_cost(current, extra, slot):
	cost = 0

	slot_start = slot.start.strftime('%H:%M')
	slot_end = slot.end.strftime('%H:%M')
	pay_percentage = slot.pay_percentage

	multiplier = 1
	if (slot_start == "12:30" and slot_end == "13:30"):
		' This is a pauzeshift '
		multiplier = 0.5
	elif (slot_start == "09:30" and slot_end == "10:30"):
		' This is an eerste uurtje shift '
		multiplier = 0.5
	elif (pay_percentage is not 100):
		' This is a shift with a different pay percentage '
		multiplier = pay_percentage / 100

	for user in current.keys():
		cost += (current[user] - extra[user]) ** 2 * multiplier
	return cost


''' Check if a worker can be assigned to a position and assigns if so '''
def assign(availability, A, D, slot, deg, current_hours):
	''' Is there actually an availability? '''
	if not availability.pk in map_pk(A[slot.pk]):
		return (D, current_hours, False)
	''' Is the user not already working on this shift? '''
	if availability.user.pk in map_user_pk(D[slot.pk]):
		return (D, current_hours, False)
	''' Update the times of new and possibly old user '''
	current_hours[availability.user.pk] += to_hours(slot.duration)
	if D[slot.pk][deg] is not None:
		current_hours[D[slot.pk][deg].user.pk] -= to_hours(slot.duration)
	''' And finally, the actual update '''
	D[slot.pk][deg] = availability
	return (D, current_hours, True)


''' Show the existing rosters '''
def show_rosters():
	for roster in Roster.objects.all():
		print ' %d: %s' % (roster.pk, roster)


''' random.choice version that uses weights '''
def weighted_choice(choices, weights):
	total = sum(weights)
	treshold = random.uniform(0, total)
	for k, weight in enumerate(weights):
		total -= weight
		if total < treshold:
			return choices[k]


