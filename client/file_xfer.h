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

#ifndef _FILE_XFER_
#define _FILE_XFER_

// FILE_XFER objects encapsulate the transfer of file
// TODO: use the HTTP Range header fields to do partial xfers

#include "types.h"
#include "http.h"

class FILE_XFER : public HTTP_OP {
public:
    double start_time;
    double end_time;
    FILE_INFO* fip;

    FILE_XFER();
    ~FILE_XFER();

    int init_download(char* url, char* outfile);
    int init_upload(char* url, char* infile);
    bool file_xfer_done;
    int file_xfer_retval;
    double elapsed_time();
};

class FILE_XFER_SET {
    vector<FILE_XFER*> file_xfers;
    HTTP_OP_SET* http_ops;
public:
    FILE_XFER_SET(HTTP_OP_SET*);
    int insert(FILE_XFER*);
    int remove(FILE_XFER*);
    bool poll();
};

#endif
