# VBoxExtPackUpdater
Download, verify and install Oracle VM VirtualBox Extension Pack with a single command

Usage
-----

Run as unprivileged user:

```
$ ./VBoxExtPackUpdater.py
[sudo] password for johndoe:
0%...10%...20%...30%...40%...50%...60%...70%...80%...90%...100%
Successfully installed "Oracle VM VirtualBox Extension Pack".
```

Run as root user:

```
# ./VBoxExtPackUpdater.py
0%...10%...20%...30%...40%...50%...60%...70%...80%...90%...100%
Successfully installed "Oracle VM VirtualBox Extension Pack".
```

Additionally, (re)build kernel modules:

```
$ ./VBoxExtPackUpdater.py --build-kernel-modules
[sudo] password for johndoe:
Stopping VirtualBox kernel modules                         [  OK  ]
Uninstalling old VirtualBox DKMS kernel modules            [  OK  ]
Trying to register the VirtualBox kernel modules using DKMS[  OK  ]
Starting VirtualBox kernel modules                         [  OK  ]
0%...10%...20%...30%...40%...50%...60%...70%...80%...90%...100%
Successfully installed "Oracle VM VirtualBox Extension Pack".
```
