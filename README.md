# UEFIReader
Tool to generate .inf payloads for use in various other UEFI projects out of an existing UEFI volume

## Download

Pre-built Windows executables are available:
- **From Releases**: Download `UEFIReader-win-x64.exe` from the [Releases](../../releases) page
- **From Actions**: Download the latest build artifact from the [Actions](../../actions) tab (workflow runs)

## Usage

```
UEFIReader.exe <Path to UEFI image/XBL image> <Output Directory>
```

## Building from Source

Requirements:
- .NET 8.0 SDK or later

Build command:
```bash
dotnet build UEFIReader.sln -c Release
```

To create a self-contained Windows executable:
```bash
dotnet publish UEFIReader/UEFIReader.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -o ./publish/win-x64
```
