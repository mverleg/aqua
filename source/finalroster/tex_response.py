
"""
	Copied from https://bitbucket.org/mverleg/django_tex_response/src/a7859552519d7145473951d6ac2109e72067a4b5?at=master
"""

from django.template.loader import render_to_string
from tempfile import mkdtemp, mkstemp
from os import remove
from os.path import join, dirname
from subprocess import Popen, PIPE
from shutil import rmtree, copy2
from django.http.response import HttpResponse
from django.template.context import RequestContext


class LatexException(Exception):
    ''' something went wrong while rendering a tex file '''


'''
    render template to .tex file
'''
def render_tex(request, template, context):
    tex_input = render_to_string(template, context, RequestContext(request))
    tmp_dir = mkdtemp()
    in_file = join(tmp_dir, 'input.tex')
    with open(in_file, 'w+') as fh:
        fh.write(tex_input)
    return in_file

'''
    render .tex file to .pdf
'''
def tex_to_pdf(tex_file, destination = mkstemp(suffix = '.pdf')[1], tex_cmd = 'lualatex', flags = ['-interaction=nonstopmode', '-halt-on-error']):
    tmp_dir = dirname(tex_file)
    out_file = join(tmp_dir, 'output.pdf')
    cmd = 'cd %s; %s %s -jobname=output input.tex' % (tmp_dir, tex_cmd, ' '.join(flags))
    proc = Popen(cmd, stdout = PIPE, stderr = PIPE, shell = True)
    outp, err = proc.communicate()
    if 'error occurred' in outp:
        raise LatexException('... ' + outp[-500:])
    if err:
        raise LatexException(err)
    try:
        copy2(out_file, destination)
    except IOError:
        raise LatexException('%s produced no error but failed to produce a pdf file; output: %s' % (tex_cmd, outp))
    rmtree(tmp_dir)
    return destination


'''
    render template to pdf-response (by using the above functions)
'''
def render_pdf(request, template, context, filename = 'file.pdf', tex_cmd = 'lualatex', flags = ['-interaction=nonstopmode', '-halt-on-error']):
    tex_file = render_tex(request, template, context)
    pdf_file = tex_to_pdf(tex_file, tex_cmd = tex_cmd, flags = flags)
    response = HttpResponse(content_type = 'application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    with open(pdf_file, 'r') as fh:
        response.write(fh.read())
    remove(pdf_file)
    return response


