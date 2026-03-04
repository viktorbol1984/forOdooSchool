===========
HR Hospital
===========

Overview
========

``hr_hospital`` is a custom Odoo module for managing a small hospital workflow:

- doctors, specialities, and schedules
- patients and patient-doctor assignment history
- visits with business constraints
- medical diagnoses and approval metadata
- diseases catalog with hierarchy and affected regions
- operational wizards and printable reports


Main Models
===========

- ``hr.hospital.visits``
- ``hr.hospital.medical.diagnosis``
- ``hr.hospital.diseases``
- ``hr.hospital.doctors``
- ``hr.hospital.doctor.speciality``
- ``hr.hospital.doctor.schedule``
- ``hr.hospital.patients``
- ``hr.hospital.contact.person``
- ``hr.hospital.patient.doctor.history``
- ``hr.hospital.abstract.person``


Wizards
=======

- ``hr.hospital.mass.reassign.doctor.wizard``
- ``hr.hospital.disease.report.wizard``
- ``hr.hospital.reschedule.visit.wizard``
- ``hr.hospital.doctor.schedule.wizard``
- ``hr.hospital.patient.card.export.wizard``


Key Business Rules
==================

- A doctor cannot be archived if active visits exist.
- Doctor rating must be between ``0.00`` and ``5.00``.
- A patient cannot have duplicate visits with the same doctor on the same day.
- Visit creation requires matching patient-doctor assignment history.
- A doctor must be available in schedule on the selected visit date.
- A visit with diagnoses cannot be deleted.


Master Data and Translations
============================

- Diseases seed data is loaded from ``data/hr_hospital_diseases_data.xml``.
- Translations for translatable master-data fields are provided in ``i18n/*.po``.


Installation
============

1. Add the module path to your Odoo ``addons_path``.
2. Update app list.
3. Install module ``HR Hospital``.

CLI example:

.. code-block:: bash

   odoo -d <db_name> -i hr_hospital --addons-path=<paths>


Run Tests
=========

Use Odoo test mode:

.. code-block:: bash

   odoo -d <db_name> -u hr_hospital --test-enable --stop-after-init --workers=0

Test files:

- ``tests/test_hr_hospital_doctors.py``
- ``tests/test_hr_hospital_visits.py``
- ``tests/test_hr_hospital_diseases.py``

