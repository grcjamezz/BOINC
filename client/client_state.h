// The contents of this file are subject to the BOINC Public License
// Version 1.0 (the "License"); you may not use this file except in
// compliance with the License. You may obtain a copy of the License at
// http://boinc.berkeley.edu/license_1.0.txt
//
// Software distributed under the License is distributed on an "AS IS"
// basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
// License for the specific language governing rights and limitations
// under the License.
//
// The Original Code is the Berkeley Open Infrastructure for Network Computing.
//
// The Initial Developer of the Original Code is the SETI@home project.
// Portions created by the SETI@home project are Copyright (C) 2002
// University of California at Berkeley. All Rights Reserved.
//
// Contributor(s):
//

#ifndef _CLIENT_STATE_
#define _CLIENT_STATE_

#include <vector>
#include <time.h>

#include "app.h"
#include "client_types.h"
#include "file_xfer.h"
#include "hostinfo.h"
#include "http.h"
#include "language.h"
#include "message.h"
#include "net_stats.h"
#include "net_xfer.h"
#include "pers_file_xfer.h"
#include "prefs.h"
#include "scheduler_op.h"
#include "ss_logic.h"
#include "time_stats.h"

#define USER_RUN_REQUEST_ALWAYS     1
#define USER_RUN_REQUEST_AUTO       2
#define USER_RUN_REQUEST_NEVER      3

// CLIENT_STATE is the global variables of the core client
// Most of the state is saved to and restored from "client_state.xml"
//
class CLIENT_STATE {
public:
    vector<PROJECT*> projects;
    vector<APP*> apps;
    vector<FILE_INFO*> file_infos;
    vector<APP_VERSION*> app_versions;
    vector<WORKUNIT*> workunits;
    vector<RESULT*> results;

    NET_XFER_SET* net_xfers;
    PERS_FILE_XFER_SET* pers_file_xfers;
    HTTP_OP_SET* http_ops;
    FILE_XFER_SET* file_xfers;
    ACTIVE_TASK_SET active_tasks;
    HOST_INFO host_info;
    GLOBAL_PREFS global_prefs;
    NET_STATS net_stats;
    SS_LOGIC ss_logic;
    LANGUAGE language;

    CLIENT_STATE();
    int init();
    int restart_tasks();
    int cleanup_and_exit();
    bool do_something();
        // Initiates and completes actions (file transfers, process executions)
        // Never blocks.
        // Returns true if it actually did something,
        // in which case it should be called again immediately.
    int net_sleep(double dt);
        // sleeps until either dt seconds have elapsed,
        // or until there's network activity.
    void parse_cmdline(int argc, char** argv);
    void parse_env_vars();
    bool time_to_exit();
    int set_nslots();
    bool should_run_cpu_benchmarks();
    int cpu_benchmarks();
	void fork_run_cpu_benchmarks();
#ifdef _WIN32
    static DWORD WINAPI win_cpu_benchmarks(LPVOID);
    HANDLE cpu_benchmarks_handle;
    DWORD cpu_benchmarks_id;
#else
    PROCESS_ID cpu_benchmarks_id;
#endif
    unsigned int cpu_benchmarks_start;
    int check_cpu_benchmarks();
    void trunc_stderr_stdout();
    double estimate_cpu_time(WORKUNIT&);
    double get_percent_done(RESULT* result);
    int project_disk_usage(PROJECT*, double&);
    int current_disk_usage(double&);
        // returns the total disk usage of BOINC on this host
    int allowed_disk_usage(double&);
    int file_xfer_giveup_period;
    bool user_idle;
    int user_run_request;
    bool start_saver;
    bool exit_when_idle;
    bool return_results_immediately;
    bool show_projects;
    bool requested_exit;
    bool use_http_proxy;
    bool use_socks_proxy;
    int proxy_server_port;
    char detach_project_url[256];
        // stores URL for -detach_project option
    char reset_project_url[256];
        // stores URL for -reset_project option
    char update_prefs_url[256];
        // stores URL for -update_prefs option
    char proxy_server_name[256];
    char socks_user_name[256];
    char socks_user_passwd[256];
    char host_venue[256];    // venue, as reported by project that sent us
        // most recent global prefs
    bool exit_before_upload;
        // exit when about to upload a file
    // exponential backoff variables
    int master_fetch_period, retry_base_period, retry_cap;
    int master_fetch_retry_cap, master_fetch_interval;
    int sched_retry_delay_min, sched_retry_delay_max;
    int pers_retry_delay_min, pers_retry_delay_max, pers_giveup;

	bool is_suspended() const { return activities_suspended; }
	bool was_previously_suspended() const { return previous_activities_suspended; }

private:
    bool client_state_dirty;
    TIME_STATS time_stats;
    int core_client_major_version;
    int core_client_minor_version;
    int old_major_version;
    int old_minor_version;
    char* platform_name;
    int nslots;
    bool skip_cpu_benchmarks;
        // if set, use hardwired numbers rather than running benchmarks
    bool run_cpu_benchmarks;
        // if set, run benchmarks on client startup
    bool activities_suspended;
	bool previous_activities_suspended;
		// if activities were suspended in the previous check_suspend();
		// this is needed to update GUI windows after suspension and close transfers/files.
    int exit_after_app_start_secs;
        // if nonzero, exit this many seconds after starting an app
    time_t app_started;
        // when the most recent app was started

    int parse_account_files();
    int parse_state_file();
    int write_state_file();
    int write_state_file_if_needed();
    int link_app(PROJECT*, APP*);
    int link_file_info(PROJECT*, FILE_INFO*);
    int link_file_ref(PROJECT*, FILE_REF*);
    int link_app_version(PROJECT*, APP_VERSION*);
    int link_workunit(PROJECT*, WORKUNIT*);
    int link_result(PROJECT*, RESULT*);
    int latest_version_num(char*);
    void check_suspend_activities(int&);
    int suspend_activities(int reason);
    int resume_activities();
    int make_project_dirs();
    int make_slot_dirs();
    bool input_files_available(RESULT*);
    int app_finished(ACTIVE_TASK&);
    bool start_apps();
    bool handle_finished_apps();
    bool handle_pers_file_xfers();
    void print_summary();
    bool garbage_collect();
    bool update_results();
    void install_global_prefs();

    // stuff related to scheduler RPCs
    //
    SCHEDULER_OP* scheduler_op;
    bool contacted_sched_server;
    void compute_resource_debts();
public:
    bool start_new_file_xfer();
    PROJECT* next_project(PROJECT*);
    PROJECT* next_project_master_pending();
    PROJECT* next_project_sched_rpc_pending();
    double work_needed_secs();
    int make_scheduler_request(PROJECT*, double);
    int handle_scheduler_reply(PROJECT*, char* scheduler_url, int& nresults);
    void set_client_state_dirty(char*);
    int report_result_error(RESULT &res, int err_num, const char *err_msg);
        // flag a result as having an error
    int add_project(char* master_url, char* authenticator);
    int reset_project(PROJECT*);
    int detach_project(PROJECT*);
private:
    PROJECT* find_project_with_overdue_results();
    RESULT* next_result_to_start() const;
    bool some_project_rpc_ok();
    bool scheduler_rpc_poll();
    void update_avg_cpu(PROJECT*);
    // double estimate_duration(WORKUNIT*);
    double current_work_buf_days();

    // the following could be eliminated by using map instead of vector
    //
public:
    PROJECT* lookup_project(char*);
    APP* lookup_app(PROJECT*, char*);
    FILE_INFO* lookup_file_info(PROJECT*, char* name);
    RESULT* lookup_result(PROJECT*, char*);
    WORKUNIT* lookup_workunit(PROJECT*, char*);
    APP_VERSION* lookup_app_version(APP*, int);
    ACTIVE_TASK* lookup_active_task_by_result(RESULT*);

    void check_project_pointer(PROJECT*);
    void check_app_pointer(APP*);
    void check_file_info_pointer(FILE_INFO*);
    void check_app_version_pointer(APP_VERSION*);
    void check_workunit_pointer(WORKUNIT*);
    void check_result_pointer(RESULT*);
    void check_pers_file_xfer_pointer(PERS_FILE_XFER*);
    void check_file_xfer_pointer(FILE_XFER*);

    void check_app(APP&);
    void check_file_info(FILE_INFO&);
    void check_file_ref(FILE_REF&);
    void check_app_version(APP_VERSION&);
    void check_workunit(WORKUNIT&);
    void check_result(RESULT&);
    void check_active_task(ACTIVE_TASK&);
    void check_pers_file_xfer(PERS_FILE_XFER&);
    void check_file_xfer(FILE_XFER&);

    void check_all();
};

extern CLIENT_STATE gstate;

#endif
