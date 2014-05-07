%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%global _pkg_name reclient

Name: re-client
Summary: Client utility for the Release Engine
Version: 0.0.0
Release: 1%{?dist}

Group: Applications/System
License: AGPLv3
Source0: %{name}-%{version}.tar.gz
Url: https://github.com/rhinception/re-client

BuildArch: noarch
BuildRequires: python2-devel
# BuildRequires: python-nose
# %{?el6:BuildRequires: python-unittest2}

%description
Utilities for interacting with the Release Engine. Supports creating,
reading, updating, and deleting playbooks.

# %check
# nosetests -v

%prep
%setup -q

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --root=$RPM_BUILD_ROOT --record=re-client-files.txt

%files -f re-client-files.txt
%dir %{python2_sitelib}/%{_pkg_name}
%{_bindir}/re-client
%doc README.md LICENSE AUTHORS

%changelog
