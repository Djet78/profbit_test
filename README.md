Task implementation notes
 - 
- I use 'iterator' queryset method in templates
  assuming that queries were not triggered before.
- Top sold product report has a bad performance, 
  I have explained it in details in the comments in 
  the 'MostPurchasedView' class.
  
  (Update): I rewrote previous solution on second branch.
  Still not perfect, but better than was. 

Routes
 - 
 - reports/time_range/
 - reports/most_purchased/
 
 