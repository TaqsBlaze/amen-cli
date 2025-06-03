## AMEN CLI - Version 0.6.0 - Release Notes

### Summary

This release focuses on significantly improving the project creation experience within AMEN CLI. We've implemented several key optimizations to reduce setup time, enhance error handling, and provide a smoother workflow for developers.

### Key Changes

*   **Optimized Project Creation Speed:**
    *   **Parallel Package Installation:** Implemented parallel package installation using `pip` to drastically reduce dependency resolution time. This allows multiple packages to be installed concurrently, speeding up the overall process.
    *   **Package Caching:** Introduced a package caching mechanism to store commonly used packages locally. This eliminates the need to download packages repeatedly for new projects, saving significant time and bandwidth.
    *   **`venv` Optimization:** Utilized the `--copies` flag when creating virtual environments with `venv`. This creates a virtual environment by copying files instead of symlinking, resulting in faster creation times, especially on Windows.
    *   **Alternative Package Installer Support:** Added experimental support for alternative package installers like `mamba` and `conda`. These installers can often resolve dependencies faster than `pip`, further accelerating project setup.
*   **Enhanced Error Handling and Robustness:**
    *   **Project Creation Rollback:** Implemented a rollback mechanism to automatically revert any changes made during project creation if an error occurs. This ensures that the system remains in a consistent state, even if the process fails partway through.
    *   **Improved Error Messages:** Enhanced error messages throughout the CLI to provide more detailed and actionable information to users. This makes it easier to diagnose and resolve issues during project creation.
    *   **Disk Space Checks:** Added checks to verify that sufficient disk space is available before starting project creation. This prevents failures due to insufficient storage and provides a more graceful user experience.
*   **New `config` Command:**
    *   Introduced a new `config` command that allows users to easily open and edit the `.env` file for a project. This provides a convenient way to manage project-specific settings and environment variables.

### Detailed Explanation of Changes

*   **Parallel Package Installation:** The `install_packages` function now uses `subprocess.run` to execute `pip install` with multiple packages specified at once. This leverages `pip`'s ability to install packages in parallel, significantly reducing the overall installation time.
*   **Package Caching:** The `_cache_packages` function now downloads packages to a local cache directory (`PACKAGE_CACHE_DIR`) before project creation. The `install_framework` function then checks if the required packages are available in the cache and installs them from there if possible.
*   **`venv` Optimization:** The `create_virtual_environment` function now uses the `--copies` flag when creating virtual environments. This creates a fully self-contained virtual environment, which can improve performance and portability.
*   **Alternative Package Installer Support:** The `install_framework` function now attempts to use `mamba` or `conda` if they are available. If these installers are not found, it falls back to using `pip`.
*   **Project Creation Rollback:** The `create_project` function now uses a `try...except` block to catch any exceptions that occur during project creation. If an exception is caught, the `rollback_creation` function is called to remove any files or directories that were created.
*   **Improved Error Messages:** Error messages throughout the CLI have been updated to provide more context and guidance to users.
*   **Disk Space Checks:** The `create_project` function now checks the available disk space before starting project creation. If insufficient space is available, an error message is displayed, and the process is aborted.
*   **`config` Command:** The new `config` command uses the `edit_file` function to open the `.env` file in the user's default text editor. This provides a convenient way to manage project-specific settings.

### Upgrade Instructions

```bash
pip install --upgrade amen-cli
```