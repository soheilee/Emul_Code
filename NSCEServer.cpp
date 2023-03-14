#include <chrono>
#include <map>
#include <string>
#include <fstream>
#include <thread>
#include <cpprest/json.h>
#include "Bus/Bus.h"
#include "Utilities/MessageUtils.h"
#include <chrono>
#include <sstream>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <exception>
#include <fcntl.h> 
#include <cstring>
#include "PhysMem.h"
#include <iostream>


/**
 * Entry point for the tool.
 *
 * @param[in] argc    The number of arguments.
 * @param[in] argv    The arguments for the tool
 *
 * @return   Completion code to indicate program completion status.
 */


static std::string MessageID, Message, FilePath;
static int StopFlag = 0;
static std::string message_Path_Received = "{\"MessageType\":\"PathReceivedSuccessfully\",\"ImmediateReplyTo\":\"nsp.reply1\",\"ContextId\":\"PathReceivedSuccessfullyID\",\"ApiLevel\":\"R&D\"}";
static std::string message_Load_Successful = "{\"MessageType\":\"FileLoadedSuccessfully\",\"ImmediateReplyTo\":\"nsp.reply1\",\"ContextId\":\"FileLoadedSuccessfullyID\",\"ApiLevel\":\"R&D\"}";
/*static std::string message_Load_Progress_20 = "{\"MessageType\":\"20\",\"ImmediateReplyTo\":\"nsp.reply1\",\"ContextId\":\"FileLoadedSuccessfullyID\",\"ApiLevel\":\"R&D\"}";
static std::string message_Load_Progress_40 = "{\"MessageType\":\"40\",\"ImmediateReplyTo\":\"nsp.reply1\",\"ContextId\":\"FileLoadedSuccessfullyID\",\"ApiLevel\":\"R&D\"}";
static std::string message_Load_Progress_60 = "{\"MessageType\":\"60\",\"ImmediateReplyTo\":\"nsp.reply1\",\"ContextId\":\"FileLoadedSuccessfullyID\",\"ApiLevel\":\"R&D\"}";
static std::string message_Load_Progress_80 = "{\"MessageType\":\"80\",\"ImmediateReplyTo\":\"nsp.reply1\",\"ContextId\":\"FileLoadedSuccessfullyID\",\"ApiLevel\":\"R&D\"}";
*/static std::vector<std::string> routingKeys = {"GUI"};
static bool Select_initialized, Load_initialized, GUI_initialized, SimulationStarted_initialized ;
int         fd;             // File descriptor of input file
PhysMem     contigBuffer;   // Manages the reserved contiguous buffer
const char* filename;       // Filename of the file we'll load into the contig buffer
static size_t bufferSize;
static std::string message_Load_Progress = "{\"MessageType\":\"80\",\"ImmediateReplyTo\":\"nsp.reply1\",\"ContextId\":\"LoadInProgressID\",\"ApiLevel\":\"R&D\"}";
static std::string Progress;
void fillBuffer(size_t fileSize);




void Publish (std::string message, int iterations, std::vector<std::string> routingKeys)
{
    nse::Bus bus("localhost", 5672, "genia", "genia123", "/", "ns3");
    for (int i = 0; i < iterations; ++i)
        {
            for (const auto& routingKey : routingKeys)
            {
                bus.publish(routingKey, nse::createEnvelope(message));
                //std::cout << "published message # " << i + 1 << " to " << routingKey << "\tresult = " << result << std::endl;
            }
        }
}
size_t getFileSize(int descriptor)
{
    // Find out how big the file is
    off64_t result = lseek64(descriptor, 0, SEEK_END);

    // Rewind back to the start of the file
    lseek(descriptor, 0, SEEK_SET);

    // And hand the size of the input-file to the caller
    return result;
}
std::string T_Subscribe (std::string queue, std::string routingKey)
{
    
    nse::Bus bus("localhost", 5672, "genia", "genia123", "/", "ns3");
    bus.subscribe(routingKey, queue, AMQP::exclusive, AMQP::noack, [](const nse::MessageEnvelope& message) 
            {
                    //printEnvelope(message);
                    //::cout << "message received = " << message.messageID() << std::endl;
                    MessageID = message.messageID();
                    Message = message.typeName();
                    
    
            });
    // Waiting here for receiving a message
    while (StopFlag==0)
    {
        if (MessageID=="GUIReady")
            {
                if (!GUI_initialized) {
                GUI_initialized = true;
                std::cout << "GUI Ready " <<std::endl;
                }
            }
        else if(MessageID=="FileSelectedID") 
            {
                FilePath = Message;      
                if (!Select_initialized) {
                Select_initialized = true;
                Publish (message_Path_Received, 1, routingKeys);
                //std::cout << "File's Path = " << FilePath << std::endl;
                }
                
            }
        else if (MessageID=="LoadFileID")
            {
                if (!Load_initialized) {
                Load_initialized = true;
                /*Load the file here*/
                filename = FilePath.c_str();
                fd = open(filename, O_RDONLY);
                if (fd < 0)
                {
                    fprintf(stderr, "Can't open %s\n", filename);
                    exit(1);
                }
                size_t fileSize = getFileSize(fd);
                if (fileSize > bufferSize) 
                {
                    fprintf(stderr, "File won't fit into contiguous buffer!\n");
                    fprintf(stderr, "  File size = %12lu bytes\n", fileSize);
                    fprintf(stderr, "Buffer size = %12lu bytes\n", bufferSize);
                    exit(1);
                }
                else
                {
                    std::cout << "Loading!!!" << std::endl;
                    fillBuffer(fileSize);
                    /*std::this_thread::sleep_for(std::chrono::milliseconds(2000));
                    Publish (message_Load_Progress_20, 1, routingKeys);
                    std::this_thread::sleep_for(std::chrono::milliseconds(2000));
                    Publish (message_Load_Progress_40, 1, routingKeys);
                    std::this_thread::sleep_for(std::chrono::milliseconds(2000));
                    Publish (message_Load_Progress_60, 1, routingKeys);
                    std::this_thread::sleep_for(std::chrono::milliseconds(2000));
                    Publish (message_Load_Progress_80, 1, routingKeys);
                    std::this_thread::sleep_for(std::chrono::milliseconds(2000));*/
                }
                
                /*getting the loading percentage here and sending it to the GUI for illustration*/




                /* When the load was complete and successful send this message*/
                Publish (message_Load_Successful, 1, routingKeys);
                //std::cout << "LoadFileID " << std::endl;
                }
                
            }
        else if (MessageID=="SimulationStarted")
        {
            if (!SimulationStarted_initialized) {
                SimulationStarted_initialized = true;
                std::cout << "SimulationStarted" << std::endl;
                }
            
        }
        else
        {
             //std::cout << "No Message yet " << std::endl;
        }
                
    }
        

    
    std::cout << StopFlag<< std::endl;
    bus.unsubscribe(routingKey, queue);
    return MessageID;
             
 
                 
}

void Execute()
{
    // Map the entire contiguous buffer
    printf("Mapping contiguous buffer\n");
    contigBuffer.map();
    // Send RabbitMQ Message to the GUI that the Buffer is loaded successfully
     // Find out how big that buffer is
    bufferSize = contigBuffer.getSize();
    std::cout << bufferSize << std::endl;
    std::string message_Mapping_Successful = "{\"MessageType\":\"ServerReady\",\"ImmediateReplyTo\":\"nsp.reply1\",\"ContextId\":\"ServerReadyID\",\"ApiLevel\":\"R&D\"}";
    Publish (message_Mapping_Successful, 1, routingKeys);

    // Separate thread for subscribe in the server
    std::thread Subs(T_Subscribe, "NSCEServer", "NSCEServer");
    Subs.join();
    
}

int main(int argc, char* argv[])
{

    
    Execute ();

    return 0;
}

void fillBuffer(size_t fileSize)
{
  
    // We will load the file into the buffer in blocks of data this size
    const uint32_t FRAME_SIZE = 0x40000000;

    // This is the number of bytes that have been loaded into the buffer
    uint64_t bytesLoaded = 0;

    // Find the physical address of the reserved contiguous buffer
    uint64_t physAddr = contigBuffer.getPhysAddr();

    // Tell the user what's taking so long...
    printf("Loading %s into RAM at address 0x%lX\n", filename, physAddr);

    // Get a pointer to the start of the contiguous buffer
    uint8_t* ptr = contigBuffer.bptr();

    // Allocate a RAM buffer in userspace
    uint8_t* localBuffer = new uint8_t[FRAME_SIZE];

    // Compute how many bytes of data to load...
    uint64_t bytesRemaining = fileSize;

    // Display the completion percentage
    printf("Percent loaded =   0");
    fflush(stdout);

    // While there is still data to load from the file...
    while (bytesRemaining)
    {
        // We'd like to load the entire remainder of the file
        size_t blockSize = bytesRemaining;

        // We're going to load this file in chunks of no more than 1 GB
        if (blockSize > FRAME_SIZE) blockSize = FRAME_SIZE;

        // Load this chunk of the file into our local user-space buffer
        size_t rc = read(fd, localBuffer, blockSize);
        if (rc != blockSize)
        {
            perror("\nread");
            exit(1);
        }

        // Copy the userspace buffer into the contiguous block of physical RAM
        memcpy(ptr, localBuffer, blockSize);

        // Bump the pointer to where the next chunk will be stored
        ptr += blockSize;

        // And keep track of how many bytes are left to load
        bytesRemaining -= blockSize;

        // Compute and display the completion percentage
        bytesLoaded += blockSize;
        int pct = 100 * bytesLoaded / fileSize;

        // Send the completion percentage to the GUI
        Progress = std::to_string(pct);
        message_Load_Progress.replace(16,2,Progress);
        Publish (message_Load_Progress, 1, routingKeys);

        // Print the completion percentage in the terminal
        printf("\b\b\b%3i", pct);
        fflush(stdout);
    }

    // Free up the localBuffer so we don't leak memory
    delete[] localBuffer;
}