---
id: 329
title: 'How To Podcast For Free'
date: '2016-08-28T19:11:36+00:00'
author: Frank
excerpt: '<p>Over the last two years I''ve learned how to podcast for free. To help you get started, I''m going to share my method with you today!</p>'
layout: post
guid: 'https://34.95.34.211/?p=329'
permalink: /2016/8/28/how-to-podcast-for-free/
thumbnail: "/assets/images/2016/08/podcast3.jpg"
categories:
    - Internet
    - Media
    - 'New Media'
    - Podcasts
    - Technology
tags:
    - 'How to podcast for free'
    - Podcasts
---

![Learn how to podcast for free with online tools available to anyone.]({{site.url}}{{site.baseurl}}/assets/images/2016/08/image-asset.jpg)<span style="font-size:12px">Learn how to podcast for free with online tools available to anyone.</span>

Back when my friend Tim and I were starting the first podcast on our *[Thought Bubble Audio](http://thoughtbubbleaudio.com)* network, we didn’t have much of a budget, so we had to get creative and figure out how to podcast for free. Sure, there are pretty reasonably-priced hosting options like *[Libsyn](https://www.libsyn.com/)* and *[Soundcloud](https://soundcloud.com/for/podcasting)*, but they have limits. We were really starting from scratch, and I was willing to put in a little bit of setup work for a free solution that I could be happy with.

I had heard full-time podcaster *[Tom Merritt](https://twitter.com/acedtect)* mention that two of his shows, *[Cordkillers](http://www.cordkillers.com/)* and *[The Daily Tech News Show](http://www.dailytechnewsshow.com/)*, are hosted for free on *[Archive.org](http://Archive.org)*, and I was intrigued. If a professional podcaster was using free tools, why couldn’t I? I did some Googling, but couldn’t find a solid, satisfying guide on how to podcast for free, so I decided to go ahead and piece together a solution based on the bits and pieces I was finding scattered all over the internet. Over the last two years, I’ve made some changes to the process, but the basics are still the same. We now host all of our shows — *[Beer With Geeks](http://www.beerwithgeeks.com/)*, *[Supergirl TV Talk](http://www.supergirltvtalk.com/)*, and *[The Marketers Next Door](http://www.marketersnextdoor.com/)* — using this method, totally for free.

To help you get started, I’m going to share that method with you today. This is everything I’ve figured out over the last two years. If you follow these steps, you’ll learn how to podcast for free. I’ll start off with the basics and then cover a few extra things you should know.

### Create a Blog

Even if you don’t want to maintain a public-facing website, this is how you’ll create an RSS feed that your listeners can subscribe to. Whether you choose to use this website and promote it publicly is up to you (though I do recommend it), but you’ll need to have this piece in place either way. Many people love *[WordPress](https://wordpress.com/)*, and I know from experience that *[Squarespace](https://www.squarespace.com/)* is great if you’re willing to pay. I like *[Blogger](http://blogger.com)* because it’s simple to use, it supports third-party site templates, and (of course) it’s free. Plus, it’s a *Google* product, so it has a pretty solid chance of sticking around for the long haul. Since that’s how I podcast for free, that’s what I’ll cover here.

Create a new blog and give it the title and description you want to use for your show. I always buy a .com domain for my shows, but that’s not a requirement (though again, I do recommend it). Once you’re set up, head to the *Settings* &gt; *Other* page. Set “*Allow Blog Feed*” to “*Full*” and set “*Enable Title Links and Enclosure Links*” to “*Yes*.” This lays the groundwork so that when you start uploading episodes later on, you’ll have a place to add them to your feed.

<div markdown="1" style="text-align: center;">
![How to Podcast for Free]({{site.url}}{{site.baseurl}}/assets/images/2016/08/how+to+podcast+for+free.png)
</div>

Now, visit your shiny new blog and scroll all the way to the bottom. You’ll see a link that says “*Subscribe to: Posts (Atom)*.” Click on that and grab the URL. For example, for *The Marketers Next Door*, it looks like this:
```
<http://www.marketersnextdoor.com/feeds/posts/default>
```
This is your blog’s feed. It’s a subscriber-friendly way to deliver the content of your blog so that other websites and devices can understand it, including podcast apps. Now, I learned the hard way that unless you give the feed URL some special love, it will only show your most recent episodes. I don’t know about you, but I want to make sure my listeners can go back into the archives and listen to any episode they want. So I figured out that by adding a little something to the end of my feed URL, I was able to get a full feed that goes all the way back to the beginning of my show.

Here’s what you’ll want to add to the end of your feed URL:
```
*?max-results=2000*
```
That guarantees that your last 2,000 episodes will show up in your feed. Unless you’re planning to do more than 2,000 episodes, you’re all set. So now, my feed URL for *The Marketers Next Door* looks like this:
```
http://www.marketersnextdoor.com/feeds/posts/default?max-results=2000
```

So now you’ve got your feed. That’s the first step in learning how to podcast for free. Time to make it *iTunes*-friendly.

### Make your Feed Compatible

When *Blogger* generates your podcast’s feed, it needs to undergo some treatment so that iTunes and other podcast apps are able to understand it. The best way to do that is with [Feedburner](http://feedburner.com). Signing up for *Feedburner* also gives you listener stats, and it makes it simple to keep your subscribers if you ever decide to move away from *Blogger*. Since it’s another *Google* product, I recommend signing in with the same account you used to create your blog.

<div markdown="1" style="text-align: center;">
![How to Podcast for Free]({{site.url}}{{site.baseurl}}/assets/images/2016/08/image-asset-copy.png)
</div>

Paste in your full feed URL and make sure to check the all-important “I am a podcaster!” box before clicking Next. Choose the *Feedburner* URL you want. For *The Marketers Next Door*, I chose:
```
<http://feeds.feedburner.com/marketersnextdoor>
```
Add the title and description you want for your show, opt into all measurement and tracking features so you can track your podcast’s success, and continue to click through until you finish the set up process.

Click the *Optimize* tab. *Feedburner* offers a lot of features, and it can feel intimidating, but there are only a few necessary features.

- *BrowserFriendly* makes your feed look great when someone visits it in a web browser.
- *SmartCast* lets you customize your cover art, subtitle, description, keywords for SEO, and *iTunes* categories. Be sure to select “Create podcast enclosures from links to audio files only” so that your text-only blog posts and other media don’t show up in your listeners’ podcast apps.
- *SmartFeed* will make your podcast feed compatible with any app that tries to download it.
- *Feed Image Burner* will set your podcast cover art as the default for the feed.
- *Title/Description Burner* will let you set a more full title and description for your podcast.

Set up all these features, and you’re ready to upload your first episode!

### Upload Your First Episode

Finally, you’ve recorded and edited your first podcast episode, you’ve saved the mp3, and you’re ready for the world to hear it. Time to upload it. *The Internet Archive* — a.k.a. *Archive.org* — is essentially the library for the World Wide Web. As their name suggests, they have a mission to archive everything on the internet. One way they do that is by accepting uploads of any size from anyone who makes a free account. That’s really convenient for someone learning how to podcast for free. Register your account, and click the “*Upload*” button near the upper right corner of the page. Then click the big green “*Upload Files*” button, and choose the mp3 of your episode. You’ll be presented with a page where you can enter all the metadata about your episode. I recommend filling out the episode title, description, some tags for search at a minimum. I usually also enter the creator as *Thought Bubble Audio*, and the [*Creative Commons*](https://creativecommons.org/) license I use to publish our shows, but those are totally optional. Click “*Upload and Create Your Item*” and wait as your podcast gets uploaded.

<div markdown="1" style="text-align: center;">
![How to Podcast for Free]({{site.url}}{{site.baseurl}}/assets/images/2016/08/image-asset-copy-2.png)
</div>

Once your file is uploaded, you’ll be redirected to a new page created especially for your episode. Under “*Download Options*” find the *VBR MP3* link. Right-click and copy the URL (this varies based on your browser, but it will usually say something like “Copy Link Address”). In the case of my episode of *The Marketers Next Door*, the URL is
```
https://archive.org/download/MND002_201608/MND002.mp3
```
Not very pretty, but it will work. Now we’re ready to tie it all together by creating a blog post.

### Publish Your Episode

Head back to *Blogger* and create a new blog post. The post title should be the episode title you want, and the body of your post should be the episode description. Now, remember when we turned on *Enclosure Links* in your settings? Here’s where that comes in handy.

In the “*Post settings*” section on the right side of the screen, click “*Links*” and paste the *Archive.org* URL into the “*Enclosure Links*” box. The box below should then automatically populate, though you may need to click in and out of it to make that happen.

<div markdown="1" style="text-align: center;">
![How to Podcast for Free]({{site.url}}{{site.baseurl}}/assets/images/2016/08/image-asset-copy-3.png)
</div>

Click “*Done*,” then review your post. When you’re ready, publish your blog post. You’re done! If you followed all the steps correctly, you’ve just successfully learned how to podcast for free. Congrats!

### Submit Your Podcast

Once you have a feed with at least one episode, you need to submit it to the major podcast directories like *[iTunes](https://itunespartner.apple.com/en/podcasts/overview#submitting)*, *[Google Play Music](https://play.google.com/music/podcasts/publish?u=0#)*, *[Stitcher](http://www.stitcher.com/content-providers)*, and any others you like. This helps you get distribution. Each of those sites has in-depth guides on how to submit, so I recommend checking them out for the most updated instructions.

### Things To Note

Try not to edit your blog posts after you publish them unless it’s really necessary. Podcast apps will sort the episodes by the “last edited” date. That means if you edit older posts, they will appear out of chronological order. I recommend thoroughly proofreading everything before you publish. It’s a small price to pay now that you know how to podcast for free.

While *Feedburner* provides podcast feed stats, they’re not always the most accurate. I prefer the *Podtrac* tracking service for stats. Creating an account is easy and free. Once you have a *Podtrac Publisher* account, add your *Feedburner* URL. Then, add this prefix to the beginning of all your MP3 enclosure links so *Podtrac* can track them:

*http://dts.podtrac.com/redirect.mp3/*

So to continue following the example of *The Marketers Next Door*, the full episode URL would be:
```
http://dts.podtrac.com/redirect.mp3/archive.org/download/MND002_201608/MND002.mp3
```
Once that prefix is in place, your *Podtrac Publisher Dashboard* will update every 24 hours with accurate download and audience metrics that are much more reliable than what *Feedburner* provides.

### Go Forth And Podcast!

The tools available at *Blogger*, *Feedburner*, and *Archive.org* are really powerful when you’re learning how to podcast for free. Put them all together and you’ll have your own podcast without worrying about server or bandwidth costs. That makes it easier for you to focus more on putting out a great podcast without paying unnecessary fees.

*Have you figured out how to podcast for free? What does your process look like? Did you have success with these tools?*