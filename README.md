# tvheadend-predefined-muxes-from-lyngsat
scrapping lyngsat to get up to data predefined muxes for tvheadend (only for dvb-s/s2)

next lyngsat pages has been scrapped and generated as predefined muxes (the result in `./output`):
* [Nilesat 201 at 7.0°W](https://www.lyngsat.com/Nilesat-201.html)
* [HD - Nilesat 201 at 7.0°W](https://www.lyngsat.com/hd/Nilesat-201.html)
* [Eutelsat 7 West A at 7.3°W](https://www.lyngsat.com/Eutelsat-7-West-A.html) 
* [HD - Eutelsat 7 West A at 7.3°W](https://www.lyngsat.com/hd/Eutelsat-7-West-A.html)
* [Eutelsat 8 West B at 8.0°W](https://www.lyngsat.com/Eutelsat-8-West-B.html)
* [HD - Eutelsat 8 West B at 8.0°W](https://www.lyngsat.com/hd/Eutelsat-8-West-B.html)

combine all files in output into one file \
`rm all.txt && cat * > all.txt`
