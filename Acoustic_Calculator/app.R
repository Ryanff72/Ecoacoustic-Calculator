library(tuneR)
library(shiny)
library(ggplot2)
library(seewave)
library(soundecology)

# Define UI for application that draws a histogram
ui <- fluidPage(
  
  # Application title
  titlePanel("Acoustic Calculator"),
  
  # Sidebar with a slider input for number of bins 
  sidebarLayout(
    sidebarPanel(
      selectInput("selected_index", "Select an Index Type:", 
                  choices = c("Acoustic Complexity (ACI)", 
                              "Acoustic Diversity (ADI)", 
                              "Acoustic Evenness (AEI)", 
                              "Bioacoustic Index (BiI)")),
      fileInput("input_file", "Upload Audio Files:",
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

  output$distPlot <- renderPlot({
    req(input$selected_index)
    req(input$input_file)
    
    # Read in which type of calculation the user wishes to do
    selected_index <- input$selected_index
    
    # Read the file uploaded by the user
    if (endsWith(input$input_file$name, ".wav")) {
      audio_data <- readWave(input$input_file$datapath)
    } else if (endsWith(input$input_file$name, ".mp3")) {
      audio_data <- readMP3(input$input_file$datapath)
    } else if (endsWith(input$input_file$name, ".flac")) {
      audio_data <- read.flac(input$input_file$datapath)
    } else {
      stop("Unsupported file format.")
    }
    
    # Calculate the Index Specified by the user
    if (selected_index == "Acoustic Complexity") {
      
    }
    else if (selected_index == "Acoustic Diversity")
    result <- acoustic_diversity(audio_data)
    showNotification((result$adi_right+result$adi_left)/2)
    
  })
}






# Run the application 
shinyApp(ui = ui, server = server)
