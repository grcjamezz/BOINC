// The contents of this file are subject to the Mozilla Public License
// Version 1.0 (the "License"); you may not use this file except in
// compliance with the License. You may obtain a copy of the License at
// http://www.mozilla.org/MPL/ 
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

#ifndef _TASK_
#define _TASK_

#include "windows_cpp.h"
#ifdef _WIN32
#include <afxwin.h>
#endif

#include <stdio.h>
#include <vector>

#include "client_types.h"

// Possible states of a process in an ACTIVE_TASK
#define PROCESS_UNINITIALIZED   0
#define PROCESS_RUNNING         1
#define PROCESS_EXITED          2
#define PROCESS_WAS_SIGNALED    3
#define PROCESS_EXIT_UNKNOWN    4
#define PROCESS_ABORTED         5
#define PROCESS_COULDNT_START   6
    // process exceeded time or disk limits

typedef int PROCESS_ID;

class CLIENT_STATE;

// ACTIVE_TASK represents a task in progress.
// Written to the client state file so that tasks can be restarted.
//
class ACTIVE_TASK {
public:
#ifdef _WIN32
    HANDLE pid_handle,thread_handle;
#endif
    RESULT* result;
    WORKUNIT* wup;
    APP_VERSION* app_version;
    PROCESS_ID pid;
    int slot;   // which slot (determines directory)
    int state;
    int exit_status;
    int signal;
    double fraction_done;
    double starting_cpu_time;
    double checkpoint_cpu_time;
    double current_cpu_time;
    char slot_dir[256];      // directory where process runs
    ACTIVE_TASK();
    int init(RESULT*);

    int start(bool first_time);          // start the task running
    void request_exit(int x);
        // request a task to exit.  If still there after x secs, kill
    void request_pause(int x);
        // request a task to pause.  If not paused after x secs, kill

    void suspend(bool suspend);

    bool check_app_status_files();
    double est_time_to_completion();
    bool read_stderr_file();

    int write(FILE*);
    int parse(FILE*, CLIENT_STATE*);
};

class ACTIVE_TASK_SET {
public:
    vector<ACTIVE_TASK*> active_tasks;
    int insert(ACTIVE_TASK*);
    int remove(ACTIVE_TASK*);
    ACTIVE_TASK* lookup_pid(int);
    bool poll();
    bool poll_time();
    void suspend_all();
    void unsuspend_all();
    int restart_tasks();
    void exit_tasks();
    int get_free_slot(int total_slots);

    int write(FILE*);
    int parse(FILE*, CLIENT_STATE*);
};

#endif
