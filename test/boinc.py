## $Id$

# boinc.py
#
# A set of classes for testing BOINC.  These classes let you create multiple
# projects and multiple hosts (all running on a single machine), add
# applications and work units, run the system, and verify that the results are
# correct.
#
# See doc/test.html for details

# the module MySQLdb can be installed on debian with "apt-get install python2.2-mysqldb"

# TODO: make things work if build_dir != src_dir

from version import *
from boinc_db import *
import os, sys, glob, time, shutil, re, atexit, traceback, random, signal
import MySQLdb

errors = 0

HAVE_INIT = 0
def init():
    global HAVE_INIT
    global VERBOSE, AUTO_SETUP, USER_NAME, INSTALL_METHOD, DELETE, TTY, OVERWRITE
    global PORT, PROXY_PORT, install_function
    global AUTO_SETUP_BASEDIR, MINISERV_BASEDIR, MINISERV_PORT, MINISERV_BASEURL
    global KEY_DIR, PROJECTS_DIR, CGI_DIR, HTML_DIR, HOSTS_DIR, CGI_URL, HTML_URL

    if HAVE_INIT: return
    HAVE_INIT = 1

    # TODO:  use @build_dir@ from autoconf.
    os.chdir(os.path.dirname(sys.argv[0]))
    if not os.path.exists("test_uc.py"):
        raise SystemExit('Could not find boinc_db.py')

    # VERBOSE: 0 = print nothing
    #          1 = print some (default
    #              if output is a tty, overwrite lines.
    #          2 = print all

    VERBOSE        = int(get_env_var('BOINC_TEST_VERBOSE', 1))
    AUTO_SETUP     = int(get_env_var("BOINC_TEST_AUTO_SETUP",0)) ####
    USER_NAME      = get_env_var("BOINC_TEST_USER_NAME", '') or get_env_var("USER")
    INSTALL_METHOD = get_env_var("BOINC_TEST_INSTALL_METHOD", 'hardlink').lower()
    DELETE         = get_env_var("BOINC_TEST_DELETE", 'if-successful').lower()

    TTY = os.isatty(1)
    OVERWRITE = TTY and VERBOSE==1

    PROXY_PORT = 16000 + (os.getpid() % 1000)

    if INSTALL_METHOD == 'copy':
        install_function = shutil.copy
    elif INSTALL_METHOD == 'link' or INSTALL_METHOD == 'hardlink':
        install_function = my_link
    elif INSTALL_METHOD == 'symlink' or INSTALL_METHOD == 'softlink':
        install_function = my_symlink
    else:
        fatal_error("Invalid BOINC_TEST_INSTALL_METHOD: %s"%BOINC_TEST_INSTALL_METHOD)

    if AUTO_SETUP:
        AUTO_SETUP_BASEDIR = 'run-%d'%os.getpid()
        verbose_echo(0, "Creating testbed in %s"%AUTO_SETUP_BASEDIR)
        os.mkdir(AUTO_SETUP_BASEDIR)
        try:
            os.unlink('run')
        except OSError:
            pass
        try:
            os.symlink(AUTO_SETUP_BASEDIR, 'run')
        except OSError:
            pass
        MINISERV_BASEDIR = os.path.join(os.getcwd(), AUTO_SETUP_BASEDIR)
        MINISERV_PORT    = 15000 + (os.getpid() % 1000)
        MINISERV_BASEURL = 'http://localhost:%d/' % MINISERV_PORT
        miniserver = MiniServer(MINISERV_PORT, MINISERV_BASEDIR)
        miniserver.run()
        #KEY_DIR          = os.path.join(MINISERV_BASEDIR, 'keys')
        PROJECTS_DIR     = os.path.join(MINISERV_BASEDIR, 'projects')
        CGI_DIR          = os.path.join(MINISERV_BASEDIR, 'cgi-bin')
        HTML_DIR         = os.path.join(MINISERV_BASEDIR, 'html')
        HOSTS_DIR        = os.path.join(MINISERV_BASEDIR, 'hosts')
        CGI_URL          = os.path.join(MINISERV_BASEURL, 'cgi-bin')
        HTML_URL         = os.path.join(MINISERV_BASEURL, 'html')
        PORT             = MINISERV_PORT
        map(os.mkdir, [PROJECTS_DIR, CGI_DIR, HTML_DIR, HOSTS_DIR])
    else:
        KEY_DIR      = get_env_var("BOINC_TEST_KEY_DIR")
        PROJECTS_DIR = get_env_var("BOINC_TEST_PROJECTS_DIR")
        CGI_DIR      = get_env_var("BOINC_TEST_CGI_DIR")
        HTML_DIR     = get_env_var("BOINC_TEST_HTML_DIR")
        HOSTS_DIR    = get_env_var("BOINC_TEST_HOSTS_DIR")
        CGI_URL      = get_env_var("BOINC_TEST_CGI_URL")
        HTML_URL     = get_env_var("BOINC_TEST_HTML_URL")
        m = re.compile('http://[^/]+:(\d+)/').match(HTML_URL)
        PORT = m and m.group(1) or 80

prev_overwrite = False
def verbose_echo(level, line):
    global prev_overwrite
    if level == 0:
        if prev_overwrite:
            print
        print line
        prev_overwrite = False
    elif VERBOSE >= level:
        if OVERWRITE:
            print "\r                                                                               ",
            print "\r", line,
            sys.stdout.flush()
            prev_overwrite = True
        else:
            print line

def fatal_error(msg):
    global errors
    errors += 1
    verbose_echo(0, "FATAL ERROR: "+msg)
    sys.exit(1)

def error(msg, fatal=0):
    global errors
    if fatal: fatal_error(msg)
    errors += 1
    verbose_echo(0, "ERROR: "+msg)

def verbose_sleep(msg, wait):
    front = msg + ' [sleep '
    back = ']'
    for i in range(1,wait+1):
        verbose_echo(1, msg + ' [sleep ' + ('.'*i).ljust(wait) + ']')
        time.sleep(1)

def get_env_var(name, default = None):
    value = os.environ.get(name, default)
    if value == None:
        print "Environment variable %s not defined" % name
        sys.exit(1)
    return value

def shell_call(cmd, doexec=False, failok=False):
    if doexec:
        os.execl('/bin/sh', 'sh', '-c', cmd)
        error("Command failed: "+cmd)
        os._exit(1)
    if os.system(cmd):
        error("Command failed: "+cmd, fatal=(not failok))
        return 1
    return 0

def verbose_shell_call(cmd, doexec=False, failok=False):
    verbose_echo(2, "   "+cmd)
    return shell_call(cmd, doexec, failok)

def proxerize(url, t=True):
    if t:
        r = re.compile('http://[^/]*/')
        return r.sub('http://localhost:%d/'%PROXY_PORT, url)
    else:
        return url

def destpath(src,dest):
    if dest.endswith('/'):
        return dest + os.path.basename(src)
    else:
        return dest

# my_symlink and my_link just add the filename to the exception object if one
# is raised - don't know why it's not already there
def my_symlink(src,dest):
    dest = destpath(src,dest)
    try:
        os.symlink(src,dest)
    except OSError, e:
        e.filename = dest
        raise

def my_link(src,dest):
    dest = destpath(src,dest)
    try:
        os.link(src,dest)
    except OSError, e:
        e.filename = dest
        raise

def use_cgi_proxy():
    global CGI_URL
    init()
    CGI_URL = proxerize(CGI_URL)
def use_html_proxy():
    global HTML_URL
    init()
    HTML_URL = proxerize(HTML_URL)

def check_exists(file):
    if not os.path.isfile(file):
        error("file doesn't exist: " + file)
        return 1
    return 0
def check_deleted(file):
    if os.path.isfile(file):
        error("file wasn't deleted: " + file)
        return 1
    return 0
def check_files_match(file, correct, descr=''):
    if not os.path.isfile(file):
        error("file doesn't exist: %s (needs to match %s)" % (file,correct))
        return 1
    if os.system("diff %s %s" % (file, correct)):
        error("File mismatch%s: %s %s" % (descr, file, correct))
        return 1
    else:
        verbose_echo(2, "Files match%s: %s %s" % (descr, file, correct))
        return 0

def check_program_exists(prog):
    if not os.path.isfile(prog):
        fatal_error("""
Executable not found: %s
Did you `make' yet?
""" % prog)
def check_core_client_executable():
    check_program_exists(os.path.join(SRC_DIR, 'client', CLIENT_BIN_FILENAME))
def check_app_executable(app):
    check_program_exists(os.path.join(SRC_DIR, 'apps', app))

def macro_substitute(macro, replacement, infile, outfile):
    open(outfile, 'w').write(open(infile).read().replace(macro, replacement))
def macro_substitute_inplace(macro, replacement, inoutfile):
    old = inoutfile + '.old'
    os.rename(inoutfile, old)
    macro_substitute(macro, replacement, old, inoutfile)

def make_executable(name):
    os.chmod(name, 755)
def force_symlink(src, dest):
    if os.path.exists(dest):
        os.unlink(dest)
    my_symlink(src, dest)
def rmtree(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)

def _remove_trail(s, suffix):
    if s.endswith(suffix):
        return s[:-len(suffix)]
    else:
        return s

def _url_to_filename(url):
    return _remove_trail(url.replace('http://','').replace('/','_'),'_')
def account_file_name(url):
    return 'account_' + _url_to_filename(url) + '.xml'

def run_tool(cmd):
    verbose_shell_call(os.path.join(SRC_DIR, 'tools', cmd))

def _gen_key_p(private_key, public_key):
    shell_call("%s/crypt_prog -genkey 1024 %s %s >/dev/null" % (
        os.path.join(SRC_DIR, 'lib'),
        private_key,
        public_key))
def _gen_key(key):
    _gen_key_p(key+'_private', key+'_public')

def get_int(s):
    '''Convert a string to an int; return 0 on error.'''
    try: return int(sys.argv[1])
    except: return 0

def unique(list):
    d = {}
    for i in list:
        d[i] = 1
    return d.keys()

def map_xml(dic, keys):
    if not isinstance(dic,dict):
        dic = dic.__dict__
    s = ''
    for key in keys:
        s += "<%s>%s</%s>\n" % (key, dic[key], key)
    return s[:-1]

def generate_shmem_key():
    return '0x1111%x' % random.randrange(0,2**16)

def _check_vars(dict, **names):
    for key in names:
        value = names[key]
        if not key in dict:
            if value == None:
                raise SystemExit('error in test script: required parameter "%s" not specified'%key)
            dict[key] = value
    for key in dict:
        if not key in names:
            raise SystemExit('error in test script: extraneous parameter "%s" unknown'%key)

class STARTS_WITH(str):
    pass

class MATCH_REGEXPS(list):
    def match(self, text):
        '''Returns True iff each regexp in self is in text'''
        for r in self:
            R = re.compile(r)
            if not R.search(text):
                return False
        return True
    pass

def dict_match(dic, resultdic):
    '''match values in DIC against RESULTDIC'''
    if not isinstance(dic, dict):
        dic = dic.__dict__
    for key in dic.keys():
        expected = dic[key]
        try:
            found = resultdic[key]
        except KeyError:
            error("Database query result didn't have key '%s'!" % key)
            continue
        if isinstance(expected,STARTS_WITH):
            match = found.startswith(expected)
        elif isinstance(expected,MATCH_REGEXPS):
            match = expected.match(found)
        else:
            match = found == expected
        if not match:
            id = resultdic.get('id', '?')
            if str(found).count('\n') or str(expected).count('\n'):
                format = """result %s: unexpected %s:

%s

(expected:)

%s"""
            else:
                format = "result %s: unexpected %s '%s' (expected '%s')"
            error( format % (id, key, found, expected))

def _db_query(db, query):
    db.query(query)
    result = db.use_result()
    return result and result.fetch_row(0,1)

def num_results(db, q=""):
    return _db_query(db, "select count(*) from result "+q)[0]['count(*)']
def num_wus_left(db):
    return num_results(db, "where server_state=%d"%RESULT_SERVER_STATE_UNSENT)
def num_results_done(db):
    return num_results(db, "where server_state=%d"%RESULT_SERVER_STATE_OVER)


class Platform:
    def __init__(self, name, user_friendly_name=None):
        self.name = name
        self.user_friendly_name = user_friendly_name or name

class CoreVersion:
    def __init__(self):
        self.version = 1
        self.platform = Platform(PLATFORM)
        self.exec_dir = os.path.join(SRC_DIR, 'client')
        self.exec_name = CLIENT_BIN_FILENAME

class App:
    def __init__(self, name):
        assert(name)
        self.name = name

class AppVersion:
    def __init__(self, app, version = 1):
        self.exec_names = []
        self.exec_dir = os.path.join(SRC_DIR, 'apps')
        self.exec_names = [app.name]
        self.app = app
        self.version = 1
        self.platform = Platform(PLATFORM)

class ProjectList(list):
    def run(self):   map(lambda i: i.run(), self)
    def check(self): map(lambda i: i.check(), self)
    def stop(self):  map(lambda i: i.maybe_stop(), self)
    def get_progress(self):
        s = "Running core client - results [done/total]:"
        for db in self.dbs:
            s += " [%d/%d]" % (num_results_done(db), num_results(db))
        return s
    def start_progress_meter(self):
        self.dbs = map(lambda i: i.db_open(), self)
        self.rm = ResultMeter(self.get_progress)
    def stop_progress_meter(self):
        self.rm.stop()

all_projects = ProjectList()

class Project:
    def __init__(self, works, users=None, hosts=None,
                 short_name=None, long_name=None, core_versions=None,
                 apps=None, app_versions=None, appname=None,
                 resource_share=None, redundancy=None,
                 add_to_list=True):
        init()
        if add_to_list:
            all_projects.append(self)
        self.config_options = []
        self.config_daemons = []
        self.short_name     = short_name or 'test_'+appname
        self.long_name      = long_name or 'Project ' + self.short_name.replace('_',' ').capitalize()
        self.db_passwd      = ''
        self.generate_keys  = AUTO_SETUP
        self.shmem_key      = generate_shmem_key()
        self.resource_share = resource_share or 1
        self.redundancy     = redundancy or 2
        self.output_level   = 3

        self.master_url    = os.path.join(HTML_URL         , self.short_name , '')
        self.download_url  = os.path.join(HTML_URL         , self.short_name , 'download')
        self.cgi_url       = CGI_URL
        self.upload_url    = os.path.join(self.cgi_url     , self.short_name , 'file_upload_handler')
        self.scheduler_url = os.path.join(self.cgi_url     , self.short_name , 'cgi')
        self.project_dir   = os.path.join(PROJECTS_DIR     , self.short_name)
        self.download_dir  = os.path.join(self.project_dir , 'download')
        self.upload_dir    = os.path.join(self.project_dir , 'upload')
        self.key_dir       = os.path.join(self.project_dir , 'keys')
        self.user_name     = USER_NAME
        self.db_name       = self.user_name + '_' + self.short_name
        self.project_php_file                  = 'html_user/project.inc.sample'
        self.project_specific_prefs_php_file   = 'html_user/project_specific_prefs.inc.sample'

        self.core_versions = core_versions or [CoreVersion()]
        self.app_versions  = app_versions or [AppVersion(App(appname))]
        self.apps          = apps or unique(map(lambda av: av.app, self.app_versions))
        self.platforms     = [Platform(PLATFORM)]
        self.works         = works
        self.users         = users or [User()]
        self.hosts         = hosts or [Host()]
        # convenience vars:
        self.app_version   = self.app_versions[0]
        self.app           = self.apps[0]
        self.host          = self.hosts[0]
        self.work          = self.works[0]
        self.user          = self.users[0]

        self.started = False

    def srcdir(self, *dirs):
        return apply(os.path.join,(SRC_DIR,)+dirs)
    def dir(self, *dirs):
        return apply(os.path.join,(self.project_dir,)+dirs)

    def mkdir(self, dir):
        os.mkdir(self.dir(dir))
    def chmod(self, dir):
        os.chmod(self.dir(dir), 0777)
    def copy(self, source, dest):
        '''SOURCE is relative to SOURCE_DIR; DEST is relative to project dir'''
        install_function(self.srcdir(source), self.dir(dest))
    def copyglob(self, source, dest = None, failok=False):
        dest = self.dir(dest or os.path.join(source, ''))
        for src in glob.glob(os.path.join(self.srcdir(source), '*')):
            if not os.path.isdir(src):
                install_function(src, dest)

    def run_db_script(self, script):
        shell_call('sed -e s/BOINC_DB_NAME/%s/ %s | mysql'
                   % (self.db_name, self.srcdir('db', script)))
    def db_open(self):
        return MySQLdb.connect(db=self.db_name)

    def create_keys(self):
        _gen_key(self.dir('keys/upload'))
        _gen_key(self.dir('keys/code_sign'))

    def install_project(self, scheduler_file = None):
        if not AUTO_SETUP:
            verbose_echo(1, "Deleting previous test runs")
            rmtree(self.dir())

        verbose_echo(1, "Setting up server: creating directories");
        # make the CGI writeable in case scheduler writes req/reply files

        map(self.mkdir,
            [ '', 'cgi-bin', 'bin', 'upload', 'download', 'keys', 'html_ops', 'html_user', 'log'])
        map(self.chmod,
            [ '', 'cgi-bin', 'upload', 'log' ])

        if self.generate_keys:
            verbose_echo(1, "Setting up server files: generating keys");
            self.create_keys()
        else:
            verbose_echo(1, "Setting up server files: copying keys");
            self.copyglob(KEY_DIR, os.path.join(self.key_dir,''))

        # copy the user and administrative PHP files to the project dir,
        verbose_echo(1, "Setting up server files: copying html directories")

        self.copyglob('html_user')
        self.copyglob('html_ops')
        self.copy('tools/country_select', 'html_user/')
        self.mkdir('html_user/project_specific')
        self.copy(self.project_php_file,
                  os.path.join('html_user', 'project_specific', 'project.inc'))
        self.copy(self.project_specific_prefs_php_file,
                  os.path.join('html_user', 'project_specific', 'project_specific_prefs.inc'))

        my_symlink(self.download_dir, self.dir('html_user', 'download'))

        # Copy the sched server in the cgi directory with the cgi names given
        # source_dir/html_usr/schedulers.txt
        #

        verbose_echo(1, "Setting up server files: copying cgi programs");
        r = re.compile('<scheduler>([^<]+)</scheduler>', re.IGNORECASE)
        if scheduler_file:
            f = open(self.dir('html_user', scheduler_file))
            for line in f:
                # not sure if this is what the scheduler file is supposed to
                # mean
                match = r.search(line)
                if match:
                    cgi_name = match.group(1)
                    verbose_echo(2, "Setting up server files: copying " + cgi_name);
                    install_function('sched/cgi', os.path.join('cgi-bin', cgi_name,''))
            f.close()
        else:
            scheduler_file = 'schedulers.txt'
            f = open(self.dir('html_user', scheduler_file), 'w')
            print >>f, "<scheduler>" + self.scheduler_url, "</scheduler>"
            f.close()


        # copy all the backend programs
        map(lambda (s): self.copy(os.path.join('sched', s), 'cgi-bin/'),
            [ 'cgi', 'file_upload_handler', ])
        map(lambda (s): self.copy(os.path.join('sched', s), 'bin/'),
            [ 'make_work',
              'feeder', 'timeout_check', 'validate_test',
              'file_deleter', 'assimilator', 'start', 'stop',
              'boinc_config.py',
              'grep_logs' ])

        verbose_echo(1, "Setting up database")
        map(self.run_db_script, [ 'drop.sql', 'schema.sql', 'constraints.sql' ])

        db = self.db_open()
        db.query("insert into project(short_name, long_name) values('%s', '%s')" %(
            self.short_name, self.long_name));

        verbose_echo(1, "Setting up database: adding %d user(s)" % len(self.users))
        for user in self.users:
            if user.project_prefs:
                pp = "<project_preferences>\n%s\n</project_preferences>\n" % user.project_prefs
            else:
                pp = ''
            if user.global_prefs:
                gp = "<global_preferences>\n%s\n</global_preferences>\n" % user.global_prefs
            else:
                gp = ''

            db.query(("insert into user values (0, %d, '%s', '%s', '%s', " +
                      "'Peru', '12345', 0, 0, 0, '%s', '%s', 0, 'home', '', 0, 1)") % (
                time.time(),
                user.email_addr,
                user.name,
                user.authenticator,
                gp,
                pp))

        verbose_echo(1, "Setting up database: adding %d apps(s)" % len(self.apps))
        for app in self.apps:
            check_app_executable(app.name)
            db.query("insert into app(name, create_time) values ('%s', %d)" %(
                app.name, time.time()))

        self.platforms = unique(map(lambda a: a.platform, self.app_versions))
        verbose_echo(1, "Setting up database: adding %d platform(s)" % len(self.platforms))

        db.close()

        for platform in self.platforms:
            run_tool("add platform -db_name %s -platform_name %s -user_friendly_name '%s'" %(
                self.db_name, platform.name, platform.user_friendly_name))

        verbose_echo(1, "Setting up database: adding %d core version(s)" % len(self.core_versions))
        for core_version in self.core_versions:
            run_tool(("add core_version -db_name %s -platform_name %s" +
                      " -version %s -download_dir %s -download_url %s -exec_dir %s" +
                      " -exec_files %s") %
                     (self.db_name, core_version.platform.name,
                      core_version.version,
                      self.download_dir,
                      self.download_url,
                      core_version.exec_dir,
                      core_version.exec_name))

        verbose_echo(1, "Setting up database: adding %d app version(s)" % len(self.app_versions))
        for app_version in self.app_versions:
            app = app_version.app
            cmd = ("add app_version -db_name %s -app_name '%s'" +
                   " -platform_name %s -version %s -download_dir %s -download_url %s" +
                   " -code_sign_keyfile %s -exec_dir %s -exec_files") % (
                self.db_name, app.name, app_version.platform.name,
                app_version.version,
                self.download_dir,
                self.download_url,
                os.path.join(self.key_dir, 'code_sign_private'),
                app_version.exec_dir)
            for exec_name in app_version.exec_names:
                cmd += ' ' + exec_name
            run_tool(cmd)

        verbose_echo(1, "Setting up server files: writing config files");

        config = map_xml(self,
                         [ 'db_name', 'db_passwd', 'shmem_key',
                           'key_dir', 'download_url', 'download_dir',
                           'upload_url', 'upload_dir', 'project_dir', 'user_name',
                           'cgi_url',
                           'output_level' ])
        self.config_options = config.split('\n')
        self.write_config()

        # edit "index.php" in the user HTML directory to have the right file
        # as the source for scheduler_urls; default is schedulers.txt

        macro_substitute_inplace('FILE_NAME', scheduler_file,
                                 self.dir('html_user', 'index.php'))

        # create symbolic links to the CGI and HTML directories
        verbose_echo(1, "Setting up server files: linking cgi programs")
        force_symlink(self.dir('cgi-bin'), os.path.join(CGI_DIR, self.short_name))
        force_symlink(self.dir('html_user'), os.path.join(HTML_DIR, self.short_name))
        force_symlink(self.dir('html_ops'), os.path.join(HTML_DIR, self.short_name+'_admin'))

        # show the URLs for user and admin sites
        admin_url = os.path.join("html_user", self.short_name+'_admin/')

        verbose_echo(2, "Master URL: " + self.master_url)
        verbose_echo(2, "Admin URL:  " + admin_url)

    def install_works(self):
        for work in self.works:
            work.install(self)

    def install_hosts(self):
        for host in self.hosts:
            for user in self.users:
                host.add_user(user, self)
            host.install()

    def install(self):
        self.install_project()
        self.install_works()
        self.install_hosts()

    def http_password(self, user, password):
        'Adds http password protection to the html_ops directory'
        passwd_file = self.dir('html_ops', '.htpassword')
        f = open(self.dir('html_ops', '.htaccess'), 'w')
        print >>f, "AuthName '%s Administration'" % self.long_name
        print >>f, "AuthType Basic"
        print >>f, "AuthUserFile %s" % passwd_file
        print >>f, "require valid-user"
        f.close()
        shell_call("htpassword -bc %s %s %s" % (passwd_file, user, password))

    def _disable(self, *path):
        '''Temporarily disable a file to test exponential backoff'''
        path = apply(self.dir, path)
        os.rename(path, path+'.disabled')
    def _reenable(self, *path):
        path = apply(self.dir, path)
        os.rename(path+'.disabled', path)

    def disable_masterindex(self):
        self._disable('html_user/index.php')
    def reenable_masterindex(self):
        self._reenable('html_user/index.php')
    def disable_scheduler(self, num = ''):
        self._disable('cgi-bin/cgi'+str(num))
    def reenable_scheduler(self, num = ''):
        self._reenable('cgi-bin/cgi'+str(num))
    def disable_downloaddir(self, num = ''):
        self._disable('download'+str(num))
    def reenable_downloaddir(self, num = ''):
        self._reenable('download'+str(num))
    def disable_file_upload_handler(self, num = ''):
        self._disable('cgi-bin/file_upload_handler'+str(num))
    def reenable_file_upload_handler(self, num = ''):
        self._reenable('cgi-bin/file_upload_handler'+str(num))

    def _run_sched_prog(self, prog, args='', logfile=None):
        verbose_shell_call("cd %s && ./%s %s >> %s.log 2>&1" %
                           (self.dir('bin'), prog, args, (logfile or prog)))
    def start_servers(self):
        self.started = True
        self._run_sched_prog('start', '-v --enable')
        verbose_sleep("Starting servers for project '%s'" % self.short_name, 1)
        self.read_server_pids()

    def read_server_pids(self):
        pid_dir = self.dir('pid')
        self.pids = {}
        for pidfile in glob.glob(os.path.join(pid_dir, '*.pid')):
            try:
                pid = int(open(pidfile).readline())
            except:
                pid = 0
            if pid:
                progname = os.path.split(pidfile)[1].split('.')[0]
                self.pids[progname] = pid

    def wait_server(self, progname, msg=None):
        msg = msg or "Waiting for %s to finish..."%progname
        verbose_echo(1, msg)
        os.waitpid(self.pids[progname], 0)
        verbose_echo(1, msg+" done.")

    def _build_sched_commandlines(self, progname, kwargs):
        '''Given a KWARGS dictionary build a list of command lines string depending on the program.'''
        each_app = False
        if progname == 'feeder':
            _check_vars(kwargs)
        elif progname == 'timeout_check':
            _check_vars(kwargs, app=self.app, nerror=5, ndet=5, nredundancy=5)
        elif progname == 'make_work':
            work = kwargs.get('work', self.work)
            _check_vars(kwargs, cushion=None, redundancy=self.redundancy,
                        result_template=os.path.realpath(work.result_template),
                        wu_name=work.wu_template)
        elif progname == 'validate_test':
            _check_vars(kwargs, quorum=self.redundancy)
            each_app = True
        elif progname == 'file_deleter':
            _check_vars(kwargs)
        elif progname == 'assimilator':
            _check_vars(kwargs)
            each_app = True
        else:
            raise SystemExit("test script error: invalid progname '%s'"%progname)
        cmdline = ' '.join(map(lambda k: '-%s %s'%(k,kwargs[k]), kwargs.keys()))
        if each_app:
            return map(lambda av: '-app %s %s'%(av.app.name,cmdline), self.app_versions)
        else:
            return [cmdline]

    def sched_run(self, prog, **kwargs):
        for cmdline in self._build_sched_commandlines(prog, kwargs):
            self._run_sched_prog(prog, '-d 3 -one_pass '+cmdline)
    def sched_install(self, prog, **kwargs):
        for cmdline in self._build_sched_commandlines(prog, kwargs):
            self.config_daemons.append("%s -d 3 %s" %(prog, cmdline))
            self.write_config()
    def sched_uninstall(self, prog):
        self.config_daemons = filter(lambda l: l.find(prog)==-1, self.config_daemons)
        self.write_config()

    def start_stripcharts(self):
        map(lambda l: self.copy(os.path.join('stripchart', l), 'cgi-bin/'),
            [ 'stripchart.cgi', 'stripchart', 'stripchart.cnf',
              'looper', 'db_looper', 'datafiles', 'get_load', 'dir_size' ])
        macro_substitute('BOINC_DB_NAME', self.db_name, self.srcdir('stripchart/samples/db_count'),
                         self.dir('bin/db_count'))
        make_executable(self.dir('bin/db_count'))

        self._run_sched_prog('looper'    , 'get_load 1'                            , 'get_load')
        self._run_sched_prog('db_looper' , '"result" 1'                            , 'count_results')
        self._run_sched_prog('db_looper' , '"workunit where assimilate_state=2" 1' , 'assimilated_wus')
        self._run_sched_prog('looper'    , '"dir_size ../download" 1'              , 'download_size')
        self._run_sched_prog('looper'    , '"dir_size ../upload" 1'                , 'upload_size')

    def stop(self):
        verbose_echo(1,"Stopping server(s) for project '%s'"%self.short_name)
        self._run_sched_prog('start', '-v --disable')
        self.started = False

    def maybe_stop(self):
        if self.started: self.stop()

    def write_config(self):
        f = open(self.dir('config.xml'), 'w')
        print >>f, '<boinc>'
        print >>f, '  <config>'
        for line in self.config_options:
            print >>f, "     ", line
        print >>f, '  </config>'
        print >>f, '  <daemons>'
        for daemon in self.config_daemons:
            print >>f, "       <daemon><cmd>%s</cmd></daemon>"%daemon
        print >>f, '  </daemons>'
        print >>f, '</boinc>'

    def check_results(self, matchresult, expected_count=None):
        '''MATCHRESULT should be a dictionary of columns to check, such as:

        server_state
        stderr_out
        exit_status
        '''
        expected_count = expected_count or self.redundancy
        db = self.db_open()
        rows = _db_query(db,"select * from result")
        for row in rows:
            dict_match(matchresult, row)
        db.close()
        if len(rows) != expected_count:
            error("expected %d results, but found %d" % (expected_count, len(rows)))

    def check_files_match(self, result, correct, count=None):
        '''if COUNT is specified then [0,COUNT) is mapped onto the %d in RESULT'''
        if count != None:
            errs = 0
            for i in range(count):
                errs += self.check_files_match(result%i, correct)
            return errs
        return check_files_match(self.dir(result),
                                 correct, " for project '%s'"%self.short_name)
    def check_deleted(self, file, count=None):
        if count != None:
            errs = 0
            for i in range(count):
                errs += self.check_deleted(file%i)
            return errs
        return check_deleted(self.dir(file))
    def check_exists(self, file, count=None):
        if count != None:
            errs = 0
            for i in range(count):
                errs += self.check_exists(file%i)
            return errs
        return check_exists(self.dir(file))

class User:
    '''represents an account on a particular project'''
    def __init__(self):
        self.name = 'John'
        self.email_addr = 'john@boinc.org'
        self.authenticator = "3f7b90793a0175ad0bda68684e8bd136"
        self.project_prefs = None
        self.global_prefs = None

class HostList(list):
    def run(self):   map(lambda i: i.run(), self)

all_hosts = HostList()

class Host:
    def __init__(self, add_to_list=True):
        if add_to_list:
            all_hosts.append(self)
        self.name = 'Commodore64'
        self.users = []
        self.projects = []
        self.global_prefs = None
        self.log_flags = 'log_flags.xml'
        self.host_dir = os.path.join(HOSTS_DIR, self.name)
        self.defargs = "-exit_when_idle -skip_cpu_benchmarks -debug_fake_exponential_backoff"
        # self.defargs = "-exit_when_idle -skip_cpu_benchmarks -sched_retry_delay_min 1"

    def add_user(self, user, project):
        self.users.append(user)
        self.projects.append(project)

    def dir(self, *dirs):
        return apply(os.path.join,(self.host_dir,)+dirs)

    def install(self):
        rmtree(self.dir())
        os.mkdir(self.dir())

        verbose_echo(1, "Setting up host '%s': creating account files" % self.name);
        for (user,project) in map(None,self.users,self.projects):
            filename = self.dir(account_file_name(project.master_url))
            verbose_echo(2, "Setting up host '%s': writing %s" % (self.name, filename))

            f = open(filename, "w")
            print >>f, "<account>"
            print >>f, map_xml(project, ['master_url'])
            print >>f, map_xml(user, ['authenticator'])
            if user.project_prefs:
                print >>f, user.project_prefs
            print >>f, "</account>"
            f.close()

        # copy log flags and global prefs, if any
        if self.log_flags:
            shutil.copy(self.log_flags, self.dir('log_flags.xml'))
        if self.global_prefs:
            shell_call("cp %s %s" % (self.global_prefs, self.dir('global_prefs.xml')))
            # shutil.copy(self.global_prefs, self.dir('global_prefs.xml'))

    def run(self, args='', asynch=False):
        if asynch:
            verbose_echo(1, "Running core client asynchronously")
            pid = os.fork()
            if pid: return pid
        else:
            verbose_echo(1, "Running core client")
        verbose_shell_call("cd %s && %s %s %s > client.out 2> client.err" % (
            self.dir(), os.path.join(SRC_DIR, 'client', CLIENT_BIN_FILENAME),
            self.defargs, args))
        if asynch: os._exit(0)

    def read_cpu_time_file(filename):
        try:
            return float(open(self.dir(filename)).readline())
        except:
            return 0

    def check_file_present(self, project, filename):
        check_exists(self.dir('projects',
                              _url_to_filename(project.master_url),
                              filename))

class Work:
    def __init__(self, redundancy=1):
        self.input_files = []
        self.rsc_iops = 1.8e12
        self.rsc_fpops = 1e13
        self.rsc_memory = 1e7
        self.rsc_disk = 1e7
        self.delay_bound = 1000
        self.redundancy = redundancy
        self.app = None

    def install(self, project):
        verbose_echo(1, "Installing work <%s> in project '%s'" %(
            self.wu_template, project.short_name))
        if not self.app:
            self.app = project.app_versions[0].app
        for input_file in unique(self.input_files):
            install_function(input_file, os.path.join(project.download_dir,''))

        # simulate multiple data servers by making symbolic links to the
        # download directory
        r = re.compile('<download_url/>([^<]+)<', re.IGNORECASE)
        for line in open(self.wu_template):
            match = r.search(line)
            if match:
                newdir = project.download_dir+match.group(1)
                verbose_echo(2, "Linking "+newdir)
                os.symlink(project.download_dir, newdir)

        # simulate multiple data servers by making copies of the file upload
        # handler
        r = re.compile('<upload_url/>([^<]+)<', re.IGNORECASE)
        for line in open(self.wu_template):
            match = r.search(line)
            if match:
                handler = project.srcdir('sched', 'file_upload_handler')
                newhandler = handler + match.group(1)
                verbose_echo(2, "Linking "+newhandler)
                os.symlink(handler, newhandler)

        cmd = "create_work -db_name %s -download_dir %s -upload_url %s -download_url %s -keyfile %s -appname %s -rsc_iops %.0f -rsc_fpops %.0f -rsc_disk %.0f -wu_template %s -result_template %s -redundancy %s -wu_name %s -delay_bound %d" % (
            project.db_name, project.download_dir, project.upload_url,
            project.download_url, os.path.join(project.key_dir,'upload_private'),
            self.app.name, self.rsc_iops, self.rsc_fpops, self.rsc_disk,
            self.wu_template, self.result_template, self.redundancy, self.wu_template,
            self.delay_bound)

        for input_file in self.input_files:
            cmd += ' ' + input_file

        run_tool(cmd)

class ResultMeter:
    def __init__(self, func, args=[], delay=.1):
        '''Forks to print a progress meter'''
        self.pid = os.fork()
        if self.pid:
            atexit.register(self.stop)
            return
        while True:
            verbose_echo(1, apply(func, args))
            time.sleep(delay)
    def stop(self):
        if self.pid:
            os.kill(self.pid, 9)
            self.pid = 0

def run_check_all():
    '''Run all projects, run all hosts, check all projects, stop all projects.'''
    atexit.register(all_projects.stop)
    all_projects.run()
    all_projects.start_progress_meter()
    if os.environ.get('TEST_STOP_BEFORE_HOST_RUN'):
        raise SystemExit, 'Stopped due to $TEST_STOP_BEFORE_HOST_RUN'
    all_hosts.run()
    all_projects.stop_progress_meter()
    all_projects.check()
    all_projects.stop()

def delete_test():
    '''Delete all test data'''
    if AUTO_SETUP:
        verbose_echo(1, "Deleting testbed %s."%AUTO_SETUP_BASEDIR)
        shutil.rmtree(AUTO_SETUP_BASEDIR)

class Proxy:
    def __init__(self, code, cgi=0, html=0, start=1):
        self.pid = 0
        self.code = code
        if cgi:   use_cgi_proxy()
        if html:  use_html_proxy()
        if start: self.start()
    def start(self):
        self.pid = os.fork()
        if not self.pid:
            verbose_shell_call(
                "exec ./testproxy %d localhost:%d '%s' 2>testproxy.log" % (
                PROXY_PORT, PORT, self.code),
                doexec=True)
        verbose_sleep("Starting proxy server", 1)
        # check if child process died
        (pid,status) = os.waitpid(self.pid, os.WNOHANG)
        if pid:
            fatal_error("testproxy failed")
            self.pid = 0
        else:
            atexit.register(self.stop)
    def stop(self):
        if self.pid:
            verbose_echo(1, "Stopping proxy server")
            try:
                os.kill(self.pid, 2)
            except OSError:
                verbose_echo(0, "Couldn't kill pid %d" % self.pid)
            self.pid = 0


class MiniServer:
    def __init__(self, port, doc_root, miniserv_root=None):
        self.port = port
        self.doc_root = doc_root
        self.miniserv_root = miniserv_root or os.path.join(doc_root,'miniserv')
        if not os.path.isdir(self.miniserv_root):
            os.mkdir(self.miniserv_root)
        self.config_file = os.path.join(self.miniserv_root, 'miniserv.conf')
        self.log_file = os.path.join(self.miniserv_root, 'miniserv.log')
        self.pid_file = os.path.join(self.miniserv_root, 'miniserv.pid')
        print >>open(self.config_file,'w'), '''
root=%(doc_root)s
mimetypes=/etc/mime.types
port=%(port)d
addtype_cgi=internal/cgi
addtype_php=internal/cgi
index_docs=index.html index.htm index.cgi index.php
logfile=%(log_file)s
pidfile=%(pid_file)s
logtime=168
ssl=0
#logout=/etc/webmin/logout-flag
#libwrap=1
#alwaysresolve=1
#allow=127.0.0.1
blockhost_time=300
no_pam=0
logouttime=5
passdelay=1
blockhost_failures=3
log=1
logclear=
loghost=1
''' %self.__dict__

    def run(self):
        verbose_echo(0,"Running miniserv on localhost:%d"%self.port)
        if os.spawnl(os.P_WAIT, os.path.join(SRC_DIR, 'test/miniserv.pl'), 'miniserv', self.config_file):
            raise SystemExit("Couldn't spawn miniserv")
        atexit.register(self.stop)

    def stop(self):
        verbose_echo(1,"Killing miniserv")
        try:
            pid = int(open(self.pid_file).readline())
            os.kill(pid, signal.SIGINT)
        except Exception, e:
            print >>sys.stderr, "Couldn't stop miniserv:", e

def test_msg(msg):
    print
    print "-- Testing", msg, '-'*(66-len(msg))
    init()

def test_done():
    global errors
    init()
    if sys.__dict__.get('last_traceback'):
        if sys.last_type == KeyboardInterrupt:
            errors += 0.1
            sys.stderr.write("\nTest canceled by user\n")
        else:
            errors += 1
            sys.stderr.write("\nException thrown - bug in test scripts?\n")
    if errors:
        verbose_echo(0, "ERRORS: %d" % errors)
        if DELETE == 'always':
            delete_test()
        sys.exit(int(errors))
    else:
        verbose_echo(1, "Passed test!")
        if OVERWRITE:
            print
        if DELETE == 'if-successful' or DELETE == 'always':
            delete_test()
        if OVERWRITE:
            print
        sys.exit(0)

atexit.register(test_done)
