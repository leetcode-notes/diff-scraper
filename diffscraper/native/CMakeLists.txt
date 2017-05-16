add_library(nativediffscraper SHARED module.cpp)
target_link_libraries( nativediffscraper ${Boost_LIBRARIES} )
set_target_properties( nativediffscraper PROPERTIES PREFIX "" )

