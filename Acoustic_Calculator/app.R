library(tuneR)
library(shiny)
library(ggplot2)
library(seewave)
library(soundecology)
options(shiny.maxRequestSize = 10000 * 1024^2)

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
      fileInput("input_zip", "Upload ZIP File:")
    ),
    
    # Show a plot of the generated distribution
    mainPanel(
      textOutput("result_output")
    )
  )
)

server <- function(input, output) {
  output$result_output <- renderText({
    req(input$selected_index)
    req(input$input_zip)
    
    # Check the contents of the ZIP file
    zip_contents <- tryCatch({
      unzip_list <- unzip(input$input_zip$datapath, list = TRUE)
      unzip_list$Name
    }, error = function(e) {
      print(paste("Error accessing ZIP archive contents:", e$message))
      return(NULL)
    })
    
    print("ZIP contents:")
    print(zip_contents)
    
    if (!is.null(zip_contents)) {
      # Check if any audio files are present in the ZIP contents
      audio_files <- grep("\\.(wav|mp3|flac)$", zip_contents, value = TRUE, ignore.case = TRUE)
      
      print("Audio files found:")
      print(audio_files)
      
      if (length(audio_files) > 0) {
        # Extract files from the uploaded ZIP file
        extracted_folder <- tempfile()
        unzip(input$input_zip$datapath, exdir = extracted_folder)
        
        # List all audio files in the extracted folder
        audio_files <- list.files(extracted_folder, pattern = ".wav$|.mp3$|.flac$", full.names = TRUE)
        print("Extracted audio files:")
        print(audio_files)
        
        # Initialize a list to store formatted results for each audio file
        formatted_results <- c()
        
        # Loop through each audio file
        for (file_path in audio_files) {
          # Read the file
          if (endsWith(file_path, ".wav")) {
            audio_data <- readWave(file_path)
          } else if (endsWith(file_path, ".mp3")) {
            audio_data <- readMP3(file_path)
          } else if (endsWith(file_path, ".flac")) {
            audio_data <- read.flac(file_path)
          } else {
            stop("Unsupported file format.")
          }
          
          # Calculate the index specified by the user
          if (input$selected_index == "Acoustic Complexity (ACI)") {
            result <- acoustic_complexity(audio_data)
            if (!is.null(result$AciTotAll_left_bymin)) {
              result_value <- result$AciTotAll_left_bymin
              if (is.list(result_value)) {
                result_value <- toString(result_value) # Convert list to string
              }
              formatted_results <- c(formatted_results, paste("File:", file_path, "Acoustic Complexity:", result_value))
            } else {
              formatted_results <- c(formatted_results, paste("File:", file_path, "Acoustic Complexity: N/A"))
            }
          }
          else if (input$selected_index == "Acoustic Diversity (ADI)") {
            result <- acoustic_diversity(audio_data)
            result_value <- result$adi_left
            if (is.list(result_value)) {
              result_value <- toString(result_value) # Convert list to string
            }
            formatted_results <- c(formatted_results, paste("File:", file_path, "Acoustic Diversity:", result_value))
          }
          else if (input$selected_index == "Acoustic Evenness (AEI)") {
            result <- acoustic_evenness(audio_data, freq_step = 500)
            result_value <- result$aei_left
            print(paste("resultS!~!!: ", result_value))
            print(result_value)
            formatted_results <- c(formatted_results, paste("File:", file_path, "Bioacoustic Index:", result_value))
          }
          else if (input$selected_index == "Bioacoustic Index (BiI)") {
            result <- bioacoustic_index(audio_data)
            result_value <- result$left_area
            if (is.list(result_value)) {
              result_value <- toString(result_value) # Convert list to string
            }
            formatted_results <- c(formatted_results, paste("File:", file_path, "Bioacoustic Index:", result_value))
          }
        }
        
        return(formatted_results)
      } else {
        print("No audio files found in the ZIP archive.")
      }
    } else {
      print("Error accessing ZIP archive contents.")
    }
  })
}



shinyApp(ui = ui, server = server)

