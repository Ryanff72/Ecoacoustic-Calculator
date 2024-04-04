library(tuneR)
library(shiny)
library(ggplot2)
library(seewave)
library(soundecology)
library(future.apply)
plan(multisession)

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
      plotOutput("result_acoustic_plot")
    )
  )
)

server <- function(input, output, session) {
  
  #stop shiny app upon close
  
  session$onSessionEnded(function() { stopApp() })

  output$result_acoustic_plot <- renderPlot({
    req(input$selected_index)
    req(input$input_zip)
    start_time <- Sys.time()
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

    # Check if any audio files are present in the ZIP contents
    audio_files <- grep("\\.(wav|mp3|flac)$",
                        zip_contents,
                        value = TRUE,
                        ignore.case = TRUE)
    print("Audio files found:")
    print(audio_files)
    
    # Calculates the acoustic indices. 
    # This function is called in a multithreaded manner.
    
    calculate_index <- function(file_path, selected_index_value) {
      # Read the file
      print("Start!")
      print(file_path)
      if (endsWith(file_path, ".wav")) {
        audio_data <- readWave(file_path)
      } else if (endsWith(file_path, ".mp3")) {
        audio_data <- readMP3(file_path)
      } else if (endsWith(file_path, ".flac")) {
        audio_data <- read.flac(file_path)
      } else {
        stop("Unsupported file format.")
      }
      print("selected index:")
      print(selected_index_value)
      # Calculate the selected index
      if (selected_index_value == "Acoustic Complexity (ACI)") {
        print("FOUNDDD")
        result <- acoustic_complexity(audio_data)
        result_value <- result$AciTotAll_left_bymin
      } else if (selected_index_value == "Acoustic Diversity (ADI)") {
        result <- acoustic_diversity(audio_data)
        result_value <- result$adi_left
      } else if (selected_index_value == "Acoustic Evenness (AEI)") {
        result <- acoustic_evenness(audio_data, freq_step = 500)
        result_value <- result$aei_left
      } else if (selected_index_value == "Bioacoustic Index (BiI)") {
        result <- bioacoustic_index(audio_data)
        result_value <- result$left_area
      }
      return(result_value)
    }
    
    # Clean the temporary directory (otherwise there will be lurking files)
    
    temp_folder <- tempdir()
    extracted_folder <- file.path(temp_folder, "extracted_audio")
    if (dir.exists(extracted_folder)) {
      unlink(extracted_folder, recursive = TRUE)
    }
    
    # Extract files from the uploaded ZIP file
    
    extracted_folder <- file.path(tempdir(), "extracted_audio")
    unzip(input$input_zip$datapath, exdir = extracted_folder)
    
    # List all audio files in the extracted folder with full paths
    audio_files <- list.files(extracted_folder, pattern = ".wav$|.mp3$|.flac$", full.names = TRUE, recursive = TRUE)
    print("Extracted audio files:")
    print(audio_files)
    
    # Initialize a list to store formatted results for each audio file
    result_values <- future_lapply(audio_files,
                                   calculate_index,
                                   selected_index_value = input$selected_index)
    
    # Create a data frame with audio file names and their corresponding index values
    result_data <- data.frame(Audio_File = basename(audio_files), Index_Value = unlist(result_values))
    
    # Print runtime
    print("Run Time:")
    print(Sys.time() - start_time)
    
    # Plan for future execution
    future::plan(NULL)
    
    ggplot(result_data, aes(x = Audio_File, y = Index_Value)) +
      geom_bar(stat = "identity") +
      labs(title = "Acoustic Index Plot",
           x = "Audio File",
           y = "Index Value")
    #return(result_string)

  })
  
}
shinyApp(ui = ui, server = server)

