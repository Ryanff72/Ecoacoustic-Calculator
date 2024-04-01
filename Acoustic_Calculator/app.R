library(tuneR)
library(shiny)
library(ggplot2)
library(seewave)
library(soundecology)

# Define UI for application that draws a histogram
ui <- fluidPage(
  
  # Application title
  titlePanel("Acoustic Diversity Index"),
  
  # Sidebar with a slider input for number of bins 
  sidebarLayout(
    sidebarPanel(
      sliderInput("bins",
                  "Number of bins:",
                  min = 1,
                  max = 50,
                  value = 30),
      fileInput("input01", "Upload Audio Files:",
                accept = c(".wav", ".mp3", ".flac"))
    ),
    
    # Show a plot of the generated distribution
    mainPanel(
      plotOutput("distPlot")
    )
  )
)

server <- function(input, output) {
  # Load necessary packages
  showNotification("big boobea")
  output$distPlot <- renderPlot({
    req(input$input01)
    
    # Read the file uploaded by the user
    if (endsWith(input$input01$name, ".wav")) {
      audio_data <- readWave(input$input01$datapath)
    } else if (endsWith(input$input01$name, ".mp3")) {
      audio_data <- readMP3(input$input01$datapath)
    } else if (endsWith(input$input01$name, ".flac")) {
      audio_data <- read.flac(input$input01$datapath)
    } else {
      stop("Unsupported file format.")
    }
    result <- acoustic_diversity(audio_data)
    showNotification((result$adi_right+result$adi_left)/2)
    
  })
}






# Run the application 
shinyApp(ui = ui, server = server)
