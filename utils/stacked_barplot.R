#! /usr/bin/env Rscript
# library
library(ggplot2)


downloads <- read.csv("/home/frobledo/Software/SQANTI3/christmas_stats/download.csv")
downloads_5.3 <- downloads[downloads$Version=="v5.3.0", ]
downloads_5.3$source <- "Github releases"
docker <- read.csv("/home/frobledo/Software/SQANTI3/christmas_stats/docker.csv")
docker$source <- "Docker"
clone <- read.csv("/home/frobledo/Software/SQANTI3/christmas_stats/clone.csv")
clone$source <- "Github clones"

data <- rbind(downloads_5.3[, c(1,3,4)])
docker_data <- docker[, c(1,2,4)]
colnames(docker_data) <- colnames(data)
data <- rbind(data, docker_data)
data$Date <- sub(" .*", "", data$Date)

clone_data <- clone[, c(1,3,4)]
colnames(clone_data) <- colnames(data)
clone_data$Date <- sub("T.*","",clone_data$Date)
#clone_data <- clone_data[-39, ] 
clone_data$Date <- format(as.Date(clone_data$Date), "%d/%m/%Y" )
clone_data$Date <- sub("-","/",clone_data$Date)
clone_data$Date <- sub("-","/",clone_data$Date)
clone_data <- clone_data[35:length(clone_data$Date), ]
clone_data$Downloads <- cumsum(clone_data$Downloads)
data <- rbind(data, clone_data)
data$Date <-as.Date(data$Date, "%d/%m/%Y")

# Stacked
ggplot(data, aes(fill=source, y=Downloads, x=Date)) + 
  geom_bar(position="stack", stat="identity") +
  scale_fill_manual(values=c("#f58a53", "#fdc659", "#15918a")) +
  scale_x_date(date_labels="%d %b",date_breaks  ="1 day", limits = as.Date(c("2024-12-03", "2024-12-21"))) +
  ylab("Cumulative Downloads") +
  ggtitle("Cumulative Downloads of SQANTI3 v5.3.0") 
