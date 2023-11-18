# Analysis results
This file contains analytical summary for given repository. It consists of following sections:
- **Peak contribution times** - plots and tables showing relation between number of commits and time of a day / day of a week
- **Contributors activity** - number of commits and volume of insertions for the most active contributors
- **Messages patterns** - the most popular patterns in commit messages, both in tabular form and as 'wordcloud' plots
- **Periods of activity before merge** - relation between number of commits and time to nearest merge
- **Insertions / deletions stats** - distributions of insertions / deletions per commit in the form of histogram, plus some basic stats, such as median and avg value
- **Contributors productivity** - top contributors in terms of insertions / deletions ratio
- **Contributors activity in terms of time** - number of commits and insertions per day for given contributors

## 1. Peak contribution times
Table below shows the sum of commits per time of a day:

![commits_time_of_day_table](assets/commits_time_of_day_table.png)

The visualization of table above:

![commits_time_of_day_plot](assets/commits_time_of_day_plot.png)

Tables below shows the sum of commits per day of a week:

![commits_day_of_week_table](assets/commits_day_of_week_table.png)

The visualization of table above:

![commits_day_of_week_plot](assets/commits_day_of_week_plot.png)

## 2. Contributors activity

Table below shows the most active contributors in terms of number of commits:

![top_contributors_number_of_commits](assets/top_contributors_number_of_commits.png)

Next table shows the most active contributors in terms of number of insertions:

![top_contributors_number_of_insertions](assets/top_contributors_number_of_insertions.png)

## 3. Messages patterns

In this sections we shows top words from commit messages both in raw version (without any transformation) and after process
of stemming (excluding plural suffix, etc.)

### 3.1 Raw words

Table showing top raw words in the commit messages:
![top_raw_words_table](assets/top_raw_words_table.png)

Word cloud of raw words:

![word_cloud_raw_words](assets/word_cloud_raw_words.png)

### 3.2 words after stemming

Table showing top stemmed words in the commit messages:
![top_stemmed_words_table](assets/top_stemmed_words_table.png)

Word cloud of raw words:

![word_cloud_stemmed_words](assets/word_cloud_stemmed_words.png)

## 4. Periods of activity before merge

Table showing relation between number of commits and time to nearest merge:

![time_to_merge_table](assets/time_to_merge_table.png)

The same relation in the form of plot:

![time_to_merge_plot](assets/time_to_merge_plot.png)

## 5. Insertions / deletions distributions

Plot below show the distributions of insertions per commit in the form of histogram. Average value is shown
as green line and the median is represented by the red line:

![insertions_histogram](assets/insertions_histogram.png)

The same plot for deletions:

![deletions_histogram](assets/deletions_histogram.png)

## 6. Contributors productivity

Table showing top contributors in terms of insertions / deletions ratio:

![insertions_deletions_ratio](assets/insertions_deletions_ratio.png)

## 7. Contributors activity in terms of time

Table showing top contributors in terms of number of commits per day of activity. This measure can be 
especially helpful for assessing the work of new developers, who joined the project quite recently:

![commits_number_per_day](assets/commits_number_per_day.png)

Similar table showing number of insertions per day:

![insertions_number_per_day](assets/insertions_number_per_day.png)

# Summary
Hope this document was helpful. For more information please take a look at the dashboard.