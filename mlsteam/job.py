import os
import click
import json
import time
import subprocess
from datetime import datetime
from api import MyelindlApi, MyelindlApiError


@click.command()
@click.option('--job-name', required=True, help='job name')
@click.option('--package-path', help='package path (for package jobs)')
@click.option('--module-name', help='task entry file (for package jobs)')
@click.option('--image-tag', help='docker images name (for container jobs)')
@click.option('--dataset-path', help='dataset path used for container jobs (for container jobs)')
@click.option('--num-gpu', type=click.INT, default=1, help='number of GPU (default: 1)')
@click.argument('user-args', nargs=-1, type=click.Path())
def training(job_name, package_path, module_name, image_tag, dataset_path, num_gpu, user_args):
    dst_path = ''
    job_id = None
    project = os.getenv('PROJECT', None)
    if project is None:
        click.echo("PROJECT not defined, use '{}' as project name".format(job_name))
        project = job_name
    if package_path:
        if not os.path.exists(package_path):
            if not (package_path.startswith("ssh") or package_path.startswith("http")):
                click.echo('--package-path: {} not exists!'.format(package_path))
                return
    try:
        api = MyelindlApi()
        args = [a for a in user_args]
        remote_path = None
        remote_real_path = None
        result = api.job_create(
            project=project,
            image_tag=image_tag,
            dataset_path=dataset_path,
            job_name=job_name,
            module_name=module_name,
            pkg_path=package_path,
            num_gpu=num_gpu,
            user_args=' '.join(args),
        )
        job_id = result['id']
        if package_path:
            if (package_path.startswith("ssh://") or
                package_path.startswith("http")):
                pass
            else:
                bk_path = os.path.join("bk", job_id)
                subprocess.call("mc cp --recursive {} {}".format(package_path, bk_path), shell=True)
        click.echo('Job id: {}'.format(job_id))
        result = api.job_train(job_id)
        click.echo('Job {}: {}'.format(job_name, result))
    except MyelindlApiError as e:
        if job_id:
            api.job_delete(job_id)
        click.echo("submit failed, %s"% str(e))


@click.command()
@click.option('--json', 'is_json', default=False, help="return json format output")
def list(is_json):
    try:
        api = MyelindlApi()
        result = api.job_list()
        longest = 10
        if result['jobs']:
            longest = max(len(j['name']) for j in result['jobs'])
        if longest < 10:
            longest = 10
        if is_json:
            click.echo(json.dumps(result, indent=2, sort_keys=True)+'\n')
            return
        template = '| {:>16} | {:>%d} | {:>10} | {:>8} | {:>21} | {:>10} |'% longest
        header = template.format('id', 'name', 'project', 'status', 'create time', 'user')
        click.echo('=' * len(header))
        click.echo(header)
        click.echo('=' * len(header))
        for inst in result['jobs']:
            line = template.format(inst['id'],
                                   inst['name'],
                                   inst['project'],
                                   inst['status_history'][-1][0],
                                   datetime.fromtimestamp(inst['status_history'][0][1]).strftime("%Y %b %d, %H:%M:%S"),
                                   inst['username'])
            click.echo(line)
        click.echo('=' * len(header))
    except Exception, e:
        click.echo("submit failed, {}".format(e))


@click.command()
@click.option('--job-id', required=True, help='job id')
def log(job_id):
    try:
        api = MyelindlApi()
        click.echo(api.job_log(job_id))
    except MyelindlApiError, e:
        click.echo("failed, {}".format(e))


@click.command()
@click.option('--job-id', required=True, help='job id')
def delete(job_id):
    try:
        api = MyelindlApi()
        result = api.job_delete(job_id)
        click.echo('Job {} deleted '.format(job_id))
    except Exception, e:
        click.echo("failed, {}".format(e))


@click.command()
@click.option('--job-id', required=True, help='job id')
def abort(job_id):
    try:
        api = MyelindlApi()
        result = api.job_abort(job_id)
        click.echo('Job {} aborted '.format(job_id))
    except Exception, e:
        click.echo("failed, {}".format(e))


@click.command()
@click.option('--job-id', required=True, help='job id')
def download(job_id):
    try:
        api = MyelindlApi()
        api.job_download(job_id)
    except Exception, e:
        click.echo("failed, {}".format(e))


@click.group(help='Groups of commands to manage submit')
def submit():
    pass


submit.add_command(training)


@click.group(help='Groups of commands to manage job')
def job():
    pass


job.add_command(submit)
job.add_command(list)
job.add_command(log)
job.add_command(delete)
job.add_command(abort)
job.add_command(download)
