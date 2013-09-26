library('ggplot2')
library(foreign)
args <- commandArgs(TRUE)
# R.test.results <- read.table(args[1], header=T, sep=",", quote="")
R.test.results <- read.dta(args[1])
ggplot() +
geom_bar(aes(x=reorder(index, freq, function(x) x * -1), y=freq),
    data=R.test.results,
    stat="identity") +
scale_x_discrete("Interval") +
scale_y_continuous("Frequency") +
ggsave(args[2])
