// Berkeley Open Infrastructure for Network Computing
// http://boinc.berkeley.edu
// Copyright (C) 2005 University of California
//
// This is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation;
// either version 2.1 of the License, or (at your option) any later version.
//
// This software is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
// See the GNU Lesser General Public License for more details.
//
// To view the GNU Lesser General Public License visit
// http://www.gnu.org/copyleft/lesser.html
// or write to the Free Software Foundation, Inc.,
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#include "network.h"

class GUI_RPC_CONN {
public:
    int sock;
    char nonce[256];
    bool auth_needed;
        // if true, don't allow operations other than authentication
    bool is_local;
        // connection is from local host
    GUI_RPC_CONN(int);
    ~GUI_RPC_CONN();
    int handle_rpc();
    void handle_auth1(MIOFILE&);
    void handle_auth2(char*, MIOFILE&);
};

// authentication for GUI RPCs:
// 1) if a IPaddr-list file is found, accept only from those addrs
// 2) if a password file file is found, ALSO demand password auth

class GUI_RPC_CONN_SET {
    std::vector<GUI_RPC_CONN*> gui_rpcs;
    std::vector<int> allowed_remote_ip_addresses;
    int get_allowed_hosts();
    int get_password();
    int insert(GUI_RPC_CONN*);
public:
    int lsock;
    double time_of_last_rpc_needing_network;
        // time of the last RPC that needs network access to handle

    GUI_RPC_CONN_SET();
    char password[256];
    void get_fdset(FDSET_GROUP&, FDSET_GROUP&);
    void got_select(FDSET_GROUP&);
    int init();
    void close();
    bool recent_rpc_needs_network(double interval);
};
