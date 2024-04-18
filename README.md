# QGIS-AIMS-Plugin
QGIS Plugin for managing LINZ address information

## License

This program is released under the terms of the 3 Clause BSD license. See the 
LICENSE file for further information.

Copyright 2015 Crown copyright (c) Land Information New Zealand and the New
Zealand Government.

##Dependencies
	*Qgis 3.28 (target version)

##Installation

 This plugin is under development. As development is undertaken and finalised further documentation will be supplied. 

## Note
For testing of individual pieces, if using a conda environment, you may need a hard link between the Qt5Core_conda.dll and the normal Qt5Core.dll
`C:\windows\system32>mklink /h "C:\OSGeo4W\apps\Qt5\bin\Qt5Core_conda.dll" "C:\OSGeo4W\apps\Qt5\bin\Qt5Core.dll"`
 
## Sym Link for Development on Windows
mklink /D "C:\Users\###\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\QGIS-AIMS-Plugin" "###\QGIS-AIMS-PLUGIN\QGIS-AIMS-Plugin"