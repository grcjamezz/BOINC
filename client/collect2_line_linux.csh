#! /bin/csh

# This collect2 line is specific to the environment found on RH linux host
# shaggy (gcc version 3.2.2) as of 03/01/2004.

/usr/local/lib/gcc-lib/i686-pc-linux-gnu/3.2.2/collect2 -m elf_i386 -dynamic-linker /lib/ld-linux.so.2 -o boinc_client /usr/lib/crt1.o /usr/lib/crti.o /usr/local/lib/gcc-lib/i686-pc-linux-gnu/3.2.2/crtbegin.o -L../RSAEuro/source -L/usr/local/lib/gcc-lib/i686-pc-linux-gnu/3.2.2 -L/usr/local/lib/gcc-lib/i686-pc-linux-gnu/3.2.2/../../.. boinc_client-app.o boinc_client-check_state.o boinc_client-client_msgs.o boinc_client-client_state.o boinc_client-client_types.o boinc_client-cpu_benchmark.o boinc_client-cs_account.o boinc_client-cs_apps.o boinc_client-cs_benchmark.o boinc_client-cs_cmdline.o boinc_client-cs_files.o boinc_client-cs_prefs.o boinc_client-cs_scheduler.o boinc_client-cs_statefile.o boinc_client-cs_trickle.o boinc_client-file_names.o boinc_client-file_xfer.o boinc_client-gui_rpc_server.o boinc_client-hostinfo.o boinc_client-hostinfo_unix.o boinc_client-http.o boinc_client-log_flags.o boinc_client-main.o boinc_client-net_stats.o boinc_client-net_xfer.o boinc_client-pers_file_xfer.o boinc_client-prefs.o boinc_client-proxy.o boinc_client-scheduler_op.o boinc_client-ss_logic.o boinc_client-time_stats.o boinc_client-app_ipc.o boinc_client-crypt.o boinc_client-diagnostics.o boinc_client-exception.o boinc_client-filesys.o boinc_client-language.o boinc_client-md5_file.o boinc_client-md5.o boinc_client-msg_log.o boinc_client-parse.o boinc_client-shmem.o boinc_client-util.o -lrsaeuro -lz -Bstatic -lstdc++ -Bdynamic -lnsl -Bstatic -lstdc++ -Bdynamic -lm -lgcc_s -lgcc -lc -lgcc_s -lgcc /usr/local/lib/gcc-lib/i686-pc-linux-gnu/3.2.2/crtend.o /usr/lib/crtn.o

rm  boinc_$1_i686-pc-linux-gnu
ln boinc_client  boinc_$1_i686-pc-linux-gnu
gzip -c  boinc_$1_i686-pc-linux-gnu > boinc_$1_i686-pc-linux-gnu.gz
