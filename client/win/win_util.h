
// function declarations
int UtilGetRegKey(char *name, DWORD &keyval);
int UtilSetRegKey(char *name, DWORD value);
int UtilGetRegStr(char *name, char *str);
int UtilSetRegStr(char *name, char *str);
int UtilSetRegStartupStr(char *name, char *str);
int UtilInitOSVersion( void );

#define START_SS_MSG		"BOINC_SS_START"
#define SHOW_WIN_MSG		"BOINC_SHOW_MESSAGE"
#define RUN_MUTEX			"BOINC_MUTEX"
