%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%global _pkg_name reclient

Name: re-client
Summary: Client utility for the Release Engine
Version: 0.0.3
Release: 1%{?dist}

Group: Applications/System
License: AGPLv3
Source0: %{name}-%{version}.tar.gz
Url: https://github.com/rhinception/re-client

BuildArch: noarch
BuildRequires: python2-devel
Requires: python-pymongo
Requires: python-requests
Requires: python-pika
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
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/man1/
cp -v docs/man/man1/*.1 $RPM_BUILD_ROOT/%{_mandir}/man1/

%files -f re-client-files.txt
%dir %{python2_sitelib}/%{_pkg_name}
%{_bindir}/re-client
%doc README.md LICENSE AUTHORS
%doc %{_mandir}/man1/re-client.1*

%changelog
* Wed Jun 25 2014 Tim Bielawa <tbielawa@redhat.com> - 0.0.3-1
- Add direct download/upload options

* Tue Jun 17 2014 Tim Bielawa <tbielawa@redhat.com> - 0.0.2-2
- Add missing Requires
- Add prompt for playbook ID when starting deployments

* Thu May 22 2014 Tim Bielawa <tbielawa@redhat.com> - 0.0.2-1
- Tons of fixes/enhancements. Read the git log

* Wed May  7 2014 Tim Bielawa <tbielawa@redhat.com> - 0.0.1-1
- First release
