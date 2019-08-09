# Cleaning this up
## Main Method
1. Move Arguments to custom Parser [DONE]
2. Remove Every Assignment to parsed args (This is not storage!!) [IN PROGRESS]
3. Try to extract those 17 booleans somehow
4. Extract Constants [IN PROGRESS]
5. Extract the get key function to utils 
6. Don't use magic constants for the inputs [This will break Linus, so I guess we need to have a fallback function like translate_mode]
7. Check what boolean triggers what part of the code and then begin to extract functions