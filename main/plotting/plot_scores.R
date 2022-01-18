library(dplyr)
library(ggplot2)
library(scales)
library(gtools)
# Read changelog file into a data frame
changelog_file <- "/home/mkirsche/git/showdown/main/reformattedprogress.csv"
changelog_table <- read.table(changelog_file, header = TRUE, sep = ",")

# Convert NewTime to Date/Time object and remove the date information so it can be plotted
changelog_table$Time <- as.POSIXct(strptime(changelog_table$Value, format="%H:%M:%OS", tz = "GMT"))
op <- options(digits.secs=3)
changelog_table$hms <- format(changelog_table$Time, format = "%H:%M:%OS",tz = "GMT")
changelog_table$hms <- as.POSIXct(changelog_table$hms, format = "%H:%M:%OS", tz = "GMT")
changelog_table$hms
changelog_table

filtered_table <- changelog_table %>% filter(Type == "Speed" & Mode == "A-Side" & Chapter != "Core")
filtered_table$Chapter <- factor(filtered_table$Chapter, 
                                 levels = c(
                                   "Forsaken City",
                                   "Old Site",
                                   "Celestial Resort",
                                   "Golden Ridge",
                                   "Mirror Temple",
                                   "Reflection",
                                   "The Summit"
                                   ))

# Plot
ggplot(filtered_table, 
       aes(x= as.Date(Date, format = "%m/%d/%y"), y = hms, color = Chapter)) + geom_line() +
  xlab("Date") +
  ylab("Time") +
  scale_y_datetime(labels = date_format("%H:%M:%S")) +
  facet_grid(cols = vars(Player), rows = vars(Chapter), scales = "free") + 
  theme(
    legend.position = "None",
    plot.title = element_text(hjust = 0.5, size = 20),
    strip.text = element_text(size = 18)
    
  ) +
  ggtitle("A-Side Times")
ggsave("/home/mkirsche/git/showdown/main/plotting/asidetimes.png",width = 6,height = 12)


