library(audio)
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
      
      # Upload spot
      
      fileInput("input_zip", "Upload ZIP File:"),
      
      # Index selection
      
      selectInput("selected_index", "Select an Index Type:", 
                  choices = c("Acoustic Complexity (ACI)", 
                              "Acoustic Diversity (ADI)", 
                              "Acoustic Evenness (AEI)", 
                              "Bioacoustic Index (BiI)")),
      
      # Freq Slider
      
      sliderInput("freq_range", "Frequency Range (Hz):", 
                  min = 0, max = 20000, value = c(1000, 20000)),
      
      # Index Description text
      
      htmlOutput("index_description") 
    ),
    
    # Show a plot of the acoustic index
    
    mainPanel(
      plotOutput("result_acoustic_plot")
    )
  )
)

server <- function(input, output, session) {
  
  #stop shiny app upon close
  
  session$onSessionEnded(function() { stopApp() })
  
  # Code for the graph itself
  
  output$result_acoustic_plot <- renderPlot({
    req(input$selected_index)
    req(input$input_zip)
    start_time <- Sys.time()
    
    # Check the contents of le ZIP file
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
    y_chart_title <- NULL
    calculate_index <- function(file_path, selected_index_value) {
      
      y_chart_title <- selected_index_value

      print(file_path)
      if (endsWith(file_path, ".wav")) {
        audio_data <- readWave(file_path)
      } else if (endsWith(file_path, ".mp3")) {
        audio_data <- readMP3(file_path)
      } else if (endsWith(file_path, ".flac")) {
        audio_data <- read.flac(file_path)
      } else if (endsWith(file_path, ".ogg")) {
        audio_data <- read.ogg(file_path)
      } else if (endsWith(file_path, ".aac")) {
        audio_data <- read.aac(file_path)
      } else if (endsWith(file_path, ".aif") || endsWith(file_path, ".aiff")) {
        audio_data <- read.aiff(file_path)
      } else if (endsWith(file_path, ".au")) {
        audio_data <- read.au(file_path)
      } else if (endsWith(file_path, ".m4a")) {
        audio_data <- read.m4a(file_path)
      } else if (endsWith(file_path, ".ogg")) {
        audio_data <- read.ogg(file_path)
      } else if (endsWith(file_path, ".opus")) {
        audio_data <- read.opus(file_path)
      } else {
        stop("Unsupported file format.")
      }
      print("selected index:")
      print(selected_index_value)
      # Calculate the selected index
      if (selected_index_value == "Acoustic Complexity (ACI)") {
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
    audio_files <- list.files(extracted_folder, pattern = ".wav$|.mp3$|.flac$",
                              full.names = TRUE,
                              recursive = TRUE)
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
    
    # Order the graph with the points so that everything is in order
    
    result_data <- result_data[order(result_data$Audio_File), ]
    
    # Plot the graph with points and have a line connecting them
    
    ggplot(result_data, aes(x = Audio_File, y = Index_Value, group = 1)) +
      geom_line(stat = "identity", color = "green", size = 1.5) +
      geom_point(color = "green", size = 3) +
      labs(title = "Acoustic Index Plot",
           x = "Audio File",
           y = input$selected_index)
  })
  
  # Code for the description of the index
  
  output$index_description <- renderUI({
    index_type <- input$selected_index
    text <- ""
    if (index_type == "Acoustic Complexity (ACI)") {
      text <- "<p>The Acoustic Complexity index is <strong> calculated by 
            dividing the audiofile into small segments (bins) and then adding up
            the differences in frequency of the adjacent bins </strong> (Diaz et al.). 
            This means that
            audio files containing more diverse parts of the harmonic spectrum
            (within the minimum and maximum values) will result in a higher ACI.
            <br><br>
            The Acoustic Complexity Index (Pieretti et al., 2011) is configured
            to output the sum of the ACI over each file divided by the length
            (in minutes) of the audio file, rather than the total, as the total
            is typically difficult to read and makes comparing across different
            sized audio files impossible.</p>"
    } else if (index_type == "Acoustic Diversity (ADI)") {
      text <- "<p>ADI blurb text goes here...</p>"
    } else if (index_type == "Acoustic Evenness (AEI)") {
      text <- "<p>AEI blurb text goes here...</p>"
    } else if (index_type == "Bioacoustic Index (BiI)") {
      text <- "<p>BiI blurb text goes here...</p>"
    }
    HTML(text)
  })
  
}
shinyApp(ui = ui, server = server)

