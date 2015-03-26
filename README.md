# Headless Fabric

Headless Fabric is a wrapper around the amazing SSH module called Fabric at
http://www.fabfile.org/. This module makes using Fabric in a program easy.

Some features:
* Prevents blocking for login/password
* Enables easy host list generation at runtime
* Enables parallel execution by default
* Simple resiliency and timeout configuration
* Catches some of Fabric's sys.exit() calls

See example.py for an example of Headless Fabric usage in a program.
