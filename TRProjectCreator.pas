program TRProjectCreator;

{$mode objfpc}{$H+}

uses
  System, SysUtils, GetOpt, TProcess, RegExpr;

type
  TDirectoryScannerError = class(Exception)
  private
    FMessage: string;
  public
    constructor Create(const AMessage: string);
    property Message: string read FMessage;
  end;

  TDirectoryScanner = class
  private
    FDirectory: string;
    FFiles: TStringList;
  public
    constructor Create(const ADirectory: string);
    procedure Scan;
    property Files: TStringList read FFiles;
  end;

  TTimingDataParser = class
  private
    FFilePath: string;
  public
    constructor Create(const AFilePath: string);
    function ParseTimingData: TDictionary<string, TTuple<float, float>>;
  end;

  TProjectFolder = class
  private
    FFilePath: string;
  public
    constructor Create(const AFilePath: string);
    procedure ProjectFolderSetup;
  end;

var
  TimingDir, Mp3Dir, OutputDir: string;
  LanguageCode: string;
  Verbose: boolean;

begin
  // Parse command-line arguments
  //...

  // Create instances of TDirectoryScanner, TTimingDataParser, and TProjectFolder
  //...

  // Main logic
  //...
end.