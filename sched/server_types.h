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

#ifndef _SERVER_TYPES_
#define _SERVER_TYPES_

#include <stdio.h>
#include <vector>

#include "db.h"

struct SCHEDULER_REQUEST {
    char authenticator[256];
    char platform_name[256];
    int hostid;                 // zero if first RPC
    int core_client_version;
    int rpc_seqno;
    int work_req_seconds;
    bool want_prefs;
    unsigned int prefs_mod_time;

    HOST host;
    vector<RESULT> results;

    SCHEDULER_REQUEST();
    ~SCHEDULER_REQUEST();
    int parse(FILE*);
};

struct SCHEDULER_REPLY {
    int request_delay;          // don't request again until this time elapses
    char message[1024];
    char message_priority[256];
    int hostid;                 // send this only if nonzero.
                                // this tells client to reset rpc_seqno
    bool send_prefs;
    PREFS prefs;
    vector<APP> apps;
    vector<APP_VERSION> app_versions;
    vector<WORKUNIT>wus;
    vector<RESULT>results;
    vector<RESULT>result_acks;

    SCHEDULER_REPLY();
    ~SCHEDULER_REPLY();
    int write(FILE*);
    void insert_app_unique(APP&);
    void insert_app_version_unique(APP_VERSION&);
    void insert_workunit_unique(WORKUNIT&);
    void insert_result(RESULT&);
};

#if 0
// stores the DB tables that don't change much
//
class DB_CACHE {
    vector<PLATFORM> platforms;
    vector<APP> apps;
    vector<APP_VERSION> app_versions;
public:
    DB_CACHE();
    int read_db();
    PLATFORM* lookup_platform(char* name);
    APP* lookup_app(int id);
    APP_VERSION* lookup_app_version(int appid, int platformid, int version);
};
#endif

#endif
