# Cleaning this up
## Main Method
1. Move Arguments to custom Parser [IN PROGRESS]
2. Try to extract those 17 booleans somehow
3. Extract Constants [IN PROGRESS]
4. Extract the get key function to utils 
5. Don't use magic constants for the inputs [This will break Linus, so I guess we need to have a fallback function like translate_mode]
6. Check what boolean triggers what part of the code and then begin to extract functions