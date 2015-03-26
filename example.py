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
# Just an example of how HeadlessFabric might be used. Enjoy!
#
# Important note: You must have SSH key access to your localhost as
# HeadlessFabric disables login/password prompts to avoid blocking!


from headless_fabric import HeadlessFabric


def execute_example():
    """Just a usage example."""
    print("Initializing HeadlessFabric...")
    print("\tMaximum number of connection attempts to remote host: 3")
    print("\tCommand timeout (in seconds): 120")
    print("\tNetwork timeout (in seconds): 120")
    ssh = HeadlessFabric(conn_attempts=3, cmd_timeout=120, net_timeout=120)

    print("Executing 'ls' on localhost")
    data = ssh.execute("ls", ["localhost"])
    print(data)

    print("\nExecuting 'ls >example.out' on localhost")
    data = ssh.execute("ls >example.out", ["localhost"])

    print("\nDownloading 'example.out' to 'local_example.out'")
    ssh.get_file("localhost", "example.out", "local_example.out")
    print("\nSuccess! (You may want to delete those example files.)")


if __name__ == "__main__":
    execute_example()
