#define AppName "E舞成名重构版"
#define AppPublisher "liang"
#define AppExeName "E5CM-CG.exe"
#define Versionfilepath AddBackslash(SourcePath) + "config\app\客户端版本.json"
#define AppVersion Trim(ExecAndGetFirstLine( \
  "powershell.exe", \
  "-NoProfile -ExecutionPolicy Bypass -Command ""$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[System.Text.Encoding]::UTF8; (Get-Content -Raw -LiteralPath '" + Versionfilepath + "' | ConvertFrom-Json).version""", \
  SourcePath \
))

#if AppVersion == ""
  #expr Error("读取 config\\app\\客户端版本.json 失败，version 为空。")
#endif

[Setup]
AppId={{9E0B6D5E-6A56-4D7B-BE4C-1F6B2C8A9E11}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=E5CM-CG_Setup_{#AppVersion}
SetupIconFile=icon\自解压安装器.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#AppExeName}
DefaultDirName={userdocs}\{#AppName}
PrivilegesRequired=lowest

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"

[Dirs]
Name: "{app}\songs"
Name: "{app}\songs\diy"
Name: "{app}\songs\花式"
Name: "{app}\songs\竞速"
Name: "{app}\state"
Name: "{app}\userdata"
Name: "{app}\userdata\profile"
Name: "{app}\userdata\profile\avatars"

[InstallDelete]
Type: filesandordirs; Name: "{app}\backmovies"

[Files]
Source: "编译结果\E5CM-CG\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "编译结果\E5CM-CG\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "编译结果\E5CM-CG\backmovies\*"; DestDir: "{app}\backmovies"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "编译结果\E5CM-CG\config\*"; DestDir: "{app}\config"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "编译结果\E5CM-CG\core\*"; DestDir: "{app}\core"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "编译结果\E5CM-CG\scenes\*"; DestDir: "{app}\scenes"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "编译结果\E5CM-CG\songs\*"; DestDir: "{app}\songs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "编译结果\E5CM-CG\ui\*"; DestDir: "{app}\ui"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "编译结果\E5CM-CG\UI-img\*"; DestDir: "{app}\UI-img"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "编译结果\E5CM-CG\冷资源\*"; DestDir: "{app}\冷资源"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "编译结果\E5CM-CG\启动说明.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\卸载 {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "立即启动 {#AppName}"; Flags: nowait postinstall skipifsilent

[Code]
procedure CopyFileIfMissing(const SourcePath, TargetPath: String);
begin
  if (SourcePath = '') or (TargetPath = '') then
    exit;
  if (not FileExists(SourcePath)) or FileExists(TargetPath) then
    exit;

  ForceDirectories(ExtractFileDir(TargetPath));
  if RenameFile(SourcePath, TargetPath) then
    exit;

  FileCopy(SourcePath, TargetPath, False);
end;

procedure CopyDirContentsIfMissing(const SourceDir, TargetDir: String);
var
  FindRec: TFindRec;
  SourceItem: String;
  TargetItem: String;
  IsDirectory: Boolean;
begin
  if (SourceDir = '') or (TargetDir = '') then
    exit;
  if not DirExists(SourceDir) then
    exit;

  ForceDirectories(TargetDir);

  if FindFirst(AddBackslash(SourceDir) + '*', FindRec) then
  begin
    try
      repeat
        if (FindRec.Name <> '.') and (FindRec.Name <> '..') then
        begin
          SourceItem := AddBackslash(SourceDir) + FindRec.Name;
          TargetItem := AddBackslash(TargetDir) + FindRec.Name;
          IsDirectory := (FindRec.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0;

          if IsDirectory then
            CopyDirContentsIfMissing(SourceItem, TargetItem)
          else if not FileExists(TargetItem) then
          begin
            ForceDirectories(ExtractFileDir(TargetItem));
            FileCopy(SourceItem, TargetItem, False);
          end;
        end;
      until not FindNext(FindRec);
    finally
      FindClose(FindRec);
    end;
  end;
end;

procedure MigrateLegacyUserData();
var
  AppDir: String;
  LegacyJsonDir: String;
  ProfileDir: String;
  AvatarDir: String;
  StateDir: String;
begin
  AppDir := ExpandConstant('{app}');
  LegacyJsonDir := AddBackslash(AppDir) + 'json';
  ProfileDir := AddBackslash(AppDir) + 'userdata\profile';
  AvatarDir := AddBackslash(ProfileDir) + 'avatars';
  StateDir := AddBackslash(AppDir) + 'state';

  ForceDirectories(AvatarDir);
  ForceDirectories(StateDir);

  CopyFileIfMissing(
    AddBackslash(LegacyJsonDir) + '个人资料.json',
    AddBackslash(ProfileDir) + '个人资料.json'
  );
  CopyFileIfMissing(
    AddBackslash(LegacyJsonDir) + 'runtime_state.sqlite3',
    AddBackslash(StateDir) + 'runtime_state.sqlite3'
  );
  CopyDirContentsIfMissing(
    AddBackslash(LegacyJsonDir) + '个人资料',
    AvatarDir
  );
end;

procedure EnsureSongsSkeletonFromManifest();
var
  SongsRoot: String;
  ManifestPath: String;
  ManifestText: String;
  LineText: String;
  NewLinePos: Integer;
begin
  SongsRoot := ExpandConstant('{app}\songs');
  ForceDirectories(SongsRoot);
  ForceDirectories(AddBackslash(SongsRoot) + 'diy');
  ManifestPath := AddBackslash(SongsRoot) + '_目录骨架清单.txt';

  if not FileExists(ManifestPath) then
    exit;
  if not LoadStringFromFile(ManifestPath, ManifestText) then
    exit;

  StringChangeEx(ManifestText, #13#10, #10, True);
  StringChangeEx(ManifestText, #13, #10, True);

  while ManifestText <> '' do
  begin
    NewLinePos := Pos(#10, ManifestText);
    if NewLinePos > 0 then
    begin
      LineText := Copy(ManifestText, 1, NewLinePos - 1);
      Delete(ManifestText, 1, NewLinePos);
    end
    else
    begin
      LineText := ManifestText;
      ManifestText := '';
    end;

    LineText := Trim(LineText);
    if (LineText <> '') and (Pos('..', LineText) = 0) then
    begin
      StringChangeEx(LineText, '/', '\', True);
      if (Length(LineText) = 0) or ((LineText[1] <> '\') and (LineText[1] <> '/')) then
        ForceDirectories(AddBackslash(SongsRoot) + LineText);
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MigrateLegacyUserData();
    EnsureSongsSkeletonFromManifest();
  end;
end;
