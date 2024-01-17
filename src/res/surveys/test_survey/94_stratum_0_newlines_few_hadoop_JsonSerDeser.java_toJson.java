/**
 * Convert an object to a JSON string
 *
 * @param instance
 * 		instance to convert
 * @return a JSON string description
 * @throws JsonProcessingException
 * 		parse problems
 */ public java.lang.String toJson(T instance) throws com.fasterxml.jackson.core.JsonProcessingException {mapper.configure(com.fasterxml.jackson.databind.SerializationFeature.INDENT_OUTPUT, true);
    return mapper.writeValueAsString(instance);
}