<?php
require_once("docutil.php");
page_head("Software prerequisites");
?>

BOINC depends on various software to build, test, and run.

<h2>Operating systems</h2>

The server components run on flavors of Unix.
We develop on Solaris 2.6-2.9, Red Hat 8,
and Debian Linux stable and unstable, so those currently work out-of-the-box.
Other Unix-like systems should work without too much configuration.
<p>
Some BOINC server components (namely the feeder and scheduling server)
use shared memory.
On hosts where these run,
the operating system must have shared memory enabled,
with a maximum segment size of at least 32 MB.
How to do this depends on the operating system;
some information is
<a href=http://developer.postgresql.org/docs/postgres/kernel-resources.html>here</a>.


<h2>Other software</h2>

Required for compiling:
<ul>
  <li><b>GNU C++</b> 2.95 or 3.0 - 3.4
  <li>Other GNU development tools: gmake, gzip, etc.
</ul>

Required on the database server:
<ul>
  <li><b>MySQL server</b> 3.23+ or 4.0+
(package <code>mysql-server</code>).
Note: Transactions are only supported by MySQL 4.0+;
to use MySQL 3.23, disable &lt;use_transactions/&gt; in config.xml

</ul>
After installing and running the server,
grant permissions for your own account and for
the account under which Apache runs
('nobody' in the following; may be different on your machine):
<pre>
    mysql -u root
    grant all on *.* to yourname@localhost;
    grant all on *.* to yourname;
    grant all on *.* to nobody@localhost;
    grant all on *.* to nobody;
</pre>
Set your PATH variable to include MySQL programs
(typically /usr/local/mysql and /usr/local/mysql/bin).

<p>
Required on other server(s):
<ul>
  <li><b>Apache</b> or other webserver, with mod_ssl and PHP (package <code>apache2</code>, <code>apache</code> or <code>apache-ssl</code>)
  <li><b>PHP</b> 4.0, configured for MySQL (packages <code>php4, php4-mysql</code>)
  <li><b>MySQL client</b> (package <code>mysql-client</code>)
  <li><b>Python</b> 2.2+ (package <code>python2.3</code> or <code>python2.2</code>)
  <li><a href=http://sourceforge.net/projects/mysql-python><b>Python module MySQLdb</b></a>
    0.9.2
    (package <code>python-mysqldb</code>)
    <br>
    0.9.3 reportedly works also
    <br>
    (0.9.1 currently won't work;
     see <a href=install_python_mysqldb.txt>installation instructions</a>;
     1.0.0 and higher don't seem to work either)
  <li><a href=http://pyxml.sourceforge.net/><b>Python module xml</b></a>
      (part of most Python distributions; package <code>python-xml</code>)
</ul>

The <a href=test.php>test suite</a> simulates all servers and client on a
single machine, so to run <code>make check</code> you need most of the usual
server and client software:
<ul>
  <li><b>MySQL server</b> with permissions to create databases
  <li><b>MySQL client</b>
  <li><b>Python</b> with modules as above
  <li>Apache and PHP: can be used but not required
</ul>

Optional, required only if you change <code>*/Makefile.am</code>:
<ul>
  <li><b>automake</b> 1.7+
  <li><b>autoconf</b> 2.5+
  <li><b>m4</b>
</ul>

<p>
On Debian Linux you can install all of the above software using
<blockquote>
<code>apt-get install g++ python python-mysqldb python-xml mysql-server mysql-client apache php4 automake autoconf</code>
</blockquote>

<p>
Some info on installing BOINC on Linux is
<a href=http://torque.oncloud8.com/archives/000124.html>here</a>.

<h2>Windows client software</h2>
Required for compiling:
<ul>
  <li><b>Microsoft Visual C++</b> 7.0
</ul>
Required for creating install packages:
<ul>
  <li><b>InstallShield</b> 5.5
</ul>


<h2>Macintosh client software</h2>
Required for compiling and creating install packages:
<ul>
  <li>Development Level PPC Macintosh running OS X 10.1 or later.
  <li>July 2002 Mac OS X Developer Tools.
  <li>Installer Vise Lite 3.6 SDK(?)
</ul>


<? page_tail(); ?>
