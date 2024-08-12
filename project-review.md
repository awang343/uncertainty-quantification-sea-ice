# Summer 2024 UTRA in Review

## Project
### What I worked on
This summer, I conducted research with Dr. Daniel Watkins on the relationship between cloud cover and Arctic sea ice motion. We broke the question down into the smaller components of rotation behavior and drift speed behavior.

In the first week, I familiarized myself with the buoy position data collected from the MOSAiC expedition. I learned how the quality control/interpolation algorithm worked by reading the code, and trying it out myself on some code. Then, I worked on visualizing the sea ice concentration, and played around with the xarray multidimensional data. I found when the buoys exited the water, so that I could crop that data out. 

At the same time, I worked on looking at the rotation data. However, some of the compass measurements didn't make sense. When I looked at the compass bearing directly, it looked like there was no change throughout the entire drift journey. However, when I used a Python library to find how the angle between two buoys on the same piece of ice was changing, I noticed that it was changing a lot. I never ended up figuring out why this discrepancy existed, but I definitely want to figure this out during the semester so that we can report on rotation biases too under cloud cover.

I went forward with just the position data. I took the position series, which was matched with wind speed for the ERA5 reanalysis. I plotted a 2D histogram of wind speed against drift speed, seeing which combinations of the two variables were more common. I fitted a linear model, and plotted this on the graph. Seeing that the slope was higher for cloud covered observations, we thought it would be worth looking at drift speed ratios. We plotted the ratios at different levels, and noticed that cloud bias occurred at high wind speeds, with this effect being more pronounced in certain seasons than others. This effect almost didn't exist at low wind speeds. We also saw wider variance in drift speed ratios for lower wind speeds as well, suggesting that the linear model works better at higher wind speeds.

Finally, I took these two results and put them on the poster. I also produced a map of sea ice concentration, with buoy paths plotted on top. In addition to a real satellite image of ice, I wanted to give viewers a better visualization of the Arctic ice. I read the Arctic Report Card to prepare myself for more general questions about the Arctic climate and condition and also explain what application this research has.

Throughout the summer, I read a few research papers, and asked clarifying questions to further supplement my general knowledge about how sea ice behaves.

### UTRA Poster Presentation
The poster presentation was great. I practiced presenting before the actual event started with Mina and my neighbors. I talked to various people, including some friends and some strangers. I chatted with Professor Wilhelmus a little about my project. For people who were generally interested in the subject but didn't have a lot of experience, I answered some questions about how the Arctic is changing, and why the sea ice matters (reading the Arctic Report Card really helped with this!). I also talked with a few people who knew more about the subject (mostly from the lab), who asked some more technical questions (like how data was cleaned, how to quantify the difference in distributions, etc.). I specifically remember someone at the end, who asked a lot. A lot of his questions were about where the wind model came from originally, and how it was decided that wind and drift had a linear relationship. We also talked about the next steps regarding how more factors beyond wind were involved.

I also managed to talk to some other presenters about their projects. A few that I remember:
- Estimating galaxy size with machine learning and CV
- Reducing computational cost of comparing vectors
- Finding how nerves in the spinal cord extend into various parts of the body in the embryo stage

### Plans for the future
During the semester, I want to first learn about how more precisely deal with autocorrelation in the dataset. Then, I want to extend my results by getting reliable ice floe rotation data from the buoys and analyzing that data under cloud and clear conditions. I would also like to add sea ice concentration as another category to split my data on, in addition to season and wind speed level, which I already have. At the end, I want to be able to present some more concrete steps for how to gap fill data under cloudy conditions.

