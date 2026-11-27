Feature: Python library
  As a scientist working with volumetric and segmentation data
  I want to build customizable processing pipelines
  So that I can prepare my data for downstream applications,
  such as visualization.

  Scenario: Retrieving the library version
    When I retrieve the library version
    Then the returned version matches the installed package version
