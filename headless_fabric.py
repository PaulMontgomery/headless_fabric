# Copyright 2015 Paul Montgomery
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Headless Fabric
# ---------------
# Fabric (http://www.fabfile.org/) provides a great SSH/SCP abstraction layer with command line
# tools. Because Fabric has a default configuration that favors interactive operation, this project
# was created to provide a headless operation mode. This code is meant to be pulled into other
# projects instead of being run with the fab command line tool.
#
# Headless operation basically means that Fabric will be configured to eliminate interactive
# prompts (such as passwords, thus this project requires SSH key authentication), silences some
# of the chatty logging and traps Fabric's odd occasional sys.exit() behavior instead of raising
# an exception (we don't want Fabric causing exits in unmonitored processes).
#
# This project also implements some non-headless operation features:
# * Enables parallel execution by default
# * Enables easy, dynamic host list generation at runtime
# * Simple resiliency and timeout configuration

import logging

from fabric.api import env, execute, get, hide, put, quiet, run


# Silence the very chatty paramiko logging a bit
logging.getLogger("paramiko").setLevel(logging.ERROR)
LOG = logging.getLogger()


class HeadlessFabric(object):
    """Headless Fabric wrapper.

    This class configures Fabric to run in a headless (no prompts for passwords, no blocking
    forever on commands).
    """
    def __init__(self, conn_attempts=3, cmd_timeout=120, net_timeout=120, key_file=None,
                 gateway=None):
        LOG.info("Initializing Fabric with conn_attempts=%d, cmd_timeout=%d, net_timeout=%d, "
                 "key_file=%s, gateway=%s",
                 conn_attempts, cmd_timeout, net_timeout, key_file, gateway)
        env.connection_attempts = conn_attempts  # Num attempts to connect to a host
        env.command_timeout = cmd_timeout        # Remote command timeout in seconds
        env.timeout = net_timeout                # Network connection timeout in seconds
        env.abort_on_prompts = True              # Don't block for command line input
        env.skip_bad_hosts = True                # Don't let a bad host abort all operations
        env.parallel = True                      # Execute commands in parallel when possible
        env.gateway = gateway
        env.use_ssh_config = True
        if key_file:  # If no key_file, use normal ~/.ssh keys
            env.no_keys = True  # Disable ~/.ssh key usage to lock this down to only key_file
            env.key_filename = key_file

    def execute(self, command, host_list):
        """Inject a dynamic, runtime host list and execute a remote command via Fabric."""
        LOG.info("Executing remote command '%s' on hosts %s", command, host_list)
        return execute(self._run_fabric_command, command, hosts=host_list)

    def get_file(self, host, remote_file, local_file):
        """Transfer a remote file to a local destination."""
        LOG.info("Transferring file %s on %s to local location %s", remote_file, host, local_file)
        return execute(self._transfer_file, get, remote_file, local_file, host=host)

    def put_file(self, host, local_file, remote_file):
        """Transfer a local file to a remote destination."""
        LOG.info("Transferring local file %s to %s on host %s", local_file, remote_file, host)
        return execute(self._transfer_file, put, local_file, remote_file, host=host)

    def _transfer_file(self, transfer_func, file1, file2):
        """Handle Fabric file transfers.

        Do not call this function directly, use get/set_remote_file() instead."""
        try:
            with quiet(), hide('output', 'running', 'warnings'):
                result = transfer_func(file1, file2)
            if result.failed:
                err_str = "File transfer ({} - {}) failed with status code {}".format(
                    file1, file2, result.return_code)
                LOG.warning(err_str)
                raise RuntimeError(err_str)
            return result
        except Exception as exc:
            err_str = "File transfer ({} - {}) failed because: {}".format(file1, file2, exc)
            LOG.warning(err_str)
            raise RuntimeError(err_str)
        except SystemExit as exc:
            # SystemExit is called by Fabric if a user prompt is needed as this is disabled to
            # prevent tests from blocking
            err_str = "File transfer ({} - {}) failed because a user prompt was needed: {}".format(
                file1, file2, exc)
            LOG.warning(err_str)
            raise LookupError(err_str)

    def _run_fabric_command(self, command):
        """Execute a remote command and return the results.

        Do not call this function directly, use execute() instead which will
        dynamically configure the host list for Fabric. Fabric has interesting issues with dynamic,
        runtime-defined host lists and this indirection helps solve that issue (see Fabric docs
        regarding "Using execute with dynamically-set host lists" for details).
        """
        try:
            with quiet(), hide('output', 'running', 'warnings'):
                result = run(command)
            if result.failed:
                err_str = "Remote command '{}' failed with status code {}: {}".format(
                    command, result.return_code, result)
                LOG.warning(err_str)
                raise RuntimeError(err_str)
            return result
        except Exception as exc:
            err_str = "Remote command {} failed because '{}'".format(command, exc)
            LOG.warning(err_str)
            raise RuntimeError(err_str)
        except SystemExit as exc:
            # SystemExit is called by Fabric if a user prompt is needed as this is disabled to
            # prevent tests from blocking
            err_str = "Remote command {} failed because a user prompt was needed: {}".format(
                command, exc)
            LOG.warning(err_str)
            raise LookupError(err_str)
