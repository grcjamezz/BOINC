// $Id$
//
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
// Revision History:
//

#ifndef _VIEWMESSAGES_H_
#define _VIEWMESSAGES_H_

#if defined(__GNUG__) && !defined(__APPLE__)
#pragma interface "ViewMessages.cpp"
#endif


#include "BOINCBaseView.h"


class CMessage : public wxObject
{
public:
	CMessage();
	~CMessage();

	wxInt32  GetProjectName( wxString& strProjectName );
	wxInt32  GetPriority( wxString& strPriority  );
	wxInt32  GetTime( wxString& strTime );
	wxInt32  GetMessage( wxString& strMessage );

	wxInt32  SetProjectName( wxString& strProjectName );
	wxInt32  SetPriority( wxString& strPriority );
	wxInt32  SetTime( wxString& strTime );
	wxInt32  SetMessage( wxString& strMessage );

protected:
	wxString m_strProjectName;
	wxString m_strPriority;
	wxString m_strTime;
    wxString m_strMessage;
};

WX_DECLARE_OBJARRAY( CMessage, CMessageCache );


class CViewMessages : public CBOINCBaseView
{
    DECLARE_DYNAMIC_CLASS( CViewMessages )

public:
    CViewMessages();
    CViewMessages(wxNotebook* pNotebook);

    ~CViewMessages();

    virtual wxString        GetViewName();
    virtual char**          GetViewIcon();

protected:

    bool                    m_bTaskHeaderHidden;
    bool                    m_bTaskCopyAllHidden;
    bool                    m_bTaskCopyMessageHidden;

    bool                    m_bTipsHeaderHidden;

    wxListItemAttr*         m_pMessageInfoAttr;
    wxListItemAttr*         m_pMessageErrorAttr;

	CMessageCache           m_MessageCache;

    virtual wxInt32         GetDocCount();

    virtual wxString        OnListGetItemText( long item, long column ) const;
    virtual wxListItemAttr* OnListGetItemAttr( long item ) const;

    virtual wxString        OnDocGetItemText( long item, long column ) const;

    virtual void            OnTaskLinkClicked( const wxHtmlLinkInfo& link );
    virtual void            OnTaskCellMouseHover( wxHtmlCell* cell, wxCoord x, wxCoord y );

    virtual wxInt32         AddCacheElement();
    virtual wxInt32         EmptyCache();
    virtual wxInt32         GetCacheCount();
    virtual wxInt32         RemoveCacheElement();
    virtual wxInt32         UpdateCache( long item, long column, wxString& strNewData );

    virtual bool            EnsureLastItemVisible();

    virtual void            UpdateSelection();
    virtual void            UpdateTaskPane();

    wxInt32                 FormatProjectName( wxInt32 item, wxString& strBuffer ) const;
    wxInt32                 FormatPriority( wxInt32 item, wxString& strBuffer ) const;
    wxInt32                 FormatTime( wxInt32 item, wxString& strBuffer ) const;
    wxInt32                 FormatMessage( wxInt32 item, wxString& strBuffer ) const;

#ifndef NOCLIPBOARD
    bool                    m_bClipboardOpen;
    wxString                m_strClipboardData;
    bool                    OpenClipboard();
    wxInt32                 CopyToClipboard( wxInt32 item );
    bool                    CloseClipboard();
#endif

};


#endif

