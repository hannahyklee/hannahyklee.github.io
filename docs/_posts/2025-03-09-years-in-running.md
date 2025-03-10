---
layout: post
title:  "Years in Running"
date:   2025-03-09 17:00:00 -0700
categories: running
---

Strava's Year in Sport is a fun way to see quick highlights about your training over the past year, but the app doesn't provide a great way of comparing activities year over year. Since training blocks, while typically only weeks to months long on their own, build up over long periods of time, it's important to occasionally zoom out and look at the big picture. It's also especially comforting to see visually just how *short* a week off due to injury, sickness, or life getting in the way actually is compared to how it feels in the moment, while simultaneously seeing how consistency over time builds.

I've also just wanted to tinker around with the Strava API and see what I could come up with. For better or worse, I held this off long enough and in that time, LLMs appeared and improved. Pros: essentially all of the code was generated using tens of prompts to Claude and ChatGPT; the whole thing came together rather quickly. Cons: I'm not sure I actually got better at using JavaScript or D3.js? But regardless, it's a start. And we're starting simple here by visualizing the last five years of my Strava running data in a GitHub contributions inspired heatmap format. 

--- 
<br>
{% include running-heatmap.html %}
