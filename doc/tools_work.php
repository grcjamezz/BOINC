<?
require_once("docutil.php");
page_head("Generating work");
echo "
<h3>Template files</h3>
<p>
Workunits and results are described by <b>template files</b>,
with placeholders for their input and output filenames.
<p>
A WU template file has the form
<pre>",htmlspecialchars("
[ <file_info>...</file_info> ]
[ ... ]
<workunit>
    [ <command_line>-flags xyz</command_line> ]
    [ <env_vars>name=val&amp;name=val</env_vars> ]
    [ <max_processing>...</max_processing> ]
    [ <max_disk>...</max_disk> ]
    [ <file_ref>...</file_ref> ]
    [ ... ]
</workunit>
"), "
</pre>
The components are: 
";
list_start();
list_item(htmlspecialchars("<command_line>"),
"The command-line arguments to be passed to the main program.");
list_item(htmlspecialchars("<env_vars>"),
"A list of environment variables in the form
name=value&name=value&name=value.");
list_item(htmlspecialchars("<max_processing>"),
"Maximum processing
(measured in <a href=credit.php>Cobblestones</a>).
An instance of the computation that exceeds this bound will be aborted.
This mechanism prevents an infinite-loop bug from
indefinitely incapacitating a host.
The default is determined by the client; typically it is 1.");
list_item(htmlspecialchars("<max_disk>"),
"Maximum disk usage (in bytes).
The default is determined by the client; typically it is 1,000,000.");
list_item(htmlspecialchars("<file_ref>"),
"describes a <a href=files.php>reference</a> to an input file,
each of which is described by a <b>&lt;file_info></b> element.");
list_end();
echo"
When a workunit is created, the template file is processed as follows:
<ul>
<li>
Within a &lt;file_info> element,
&lt;number>x&lt;/number> identifies the order of the file.
It is replaced with elements giving
the filename, download URL, MD5 checksum, and size.
file.
<li>
Within a &lt;file_ref> element,
&lt;file_number>x&lt;/file_number> is replaced with the filename.
</ul>
<p>
The result file template is macro-substituted as follows:
<ul>
<li>
&lt;OUTFILE_n> is replaced with a string of the form
'wuname_resultnum_n' where wuname is the workunit name and resultnum is
the ordinal number of the result (0, 1, ...).
<li>
&lt;UPLOAD_URL> is replaced with the upload URL.
</ul>
<p>
<h3>Command-line interface</h3>
<p>
Workunits and results can be created using either a utility program
or a C++ function.
<hr>
The utility program is
<pre>
create_work
    -appname name                   // application name
    -wu_name name                   // workunit name
    -wu_template filename           // WU template filename
    -result_template filename       // result template filename
    -redundancy n                   // # of results to create
    -db_name x                      // database name
    -db_passwd x                    // database password
    -db_host x                      // database host
    -db_user x                      // database user name
    -upload_url x                   // URL for output file upload
    -download_url x                 // base URL for input file download
    -download_dir x                 // where to move input files
    -rsc_fpops x                    // est. # floating-point ops
    -rsc_iops x                     // est. # integer ops
    -rsc_memory x                   // est. RAM working set size, bytes
    -rsc_disk x                     // est. disk space required
    -keyfile x                      // path of upload private key
    -delay_bound x                  // delay bound for result completion
    infile_1 ... infile_m           // input files
</pre>
<h3>C++ function interface</h3>
<p>
The C++ library (backend_lib.C,h) provides the functions:
<pre>
int read_key_file(char* path, R_RSA_PRIVATE_KEY& key);

int create_work(
    WORKUNIT&,
    char* wu_template,                  // contents, not path
    char* result_template_filename,     // path
    int redundancy,
    char* infile_dir,                   // where input files are
    char** infiles,                     // array of input file names
    int ninfiles
    R_RSA_PRIVATE_KEY& key,             // upload authentication key
    char* upload_url,
    char* download_url
);
</pre>
<p>
<b>read_key_file()</b> reads a private key from a file.
Use this to read the file upload authentication key.
<p>
<b>create_work()</b>
creates a workunit and one or more results.
The arguments are similar to those of the utility program;
some of the information is passed in the WORKUNIT structure,
namely the following fields:
<pre>
name
appid
batch
rsc_fpops
rsc_iops
rsc_memory
rsc_disk
delay_bound
</pre>
All other fields should be zeroed.
";
page_tail();
?>
