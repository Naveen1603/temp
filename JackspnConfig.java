import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ser.DefaultSerializerProvider;
import com.fasterxml.jackson.databind.deser.DefaultDeserializationContext;
import com.fasterxml.jackson.databind.ser.SerializerFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.lang.reflect.Field;
import java.util.Map;

public class JacksonConfigurationPrinter {

    private static final Logger logger = LoggerFactory.getLogger(JacksonConfigurationPrinter.class);

    public static void main(String[] args) {
        ObjectMapper objectMapper = new ObjectMapper();

        // Build a single log message
        StringBuilder logMessage = new StringBuilder();

        // Add serialization cache info and the cached classes
        DefaultSerializerProvider serializerProvider = objectMapper.getSerializerProvider();
        if (serializerProvider != null) {
            logMessage.append("----- Serialization Cache Info -----\n");
            logMessage.append("Cache size: ").append(serializerProvider.cachedSerializersCount()).append("\n");
            logMessage.append("Cached serializer types: \n");
            logMessage.append(getCachedSerializerTypes(serializerProvider)).append("\n");
        }

        // Add deserialization cache info and the cached classes
        DefaultDeserializationContext deserializationContext = objectMapper.getDeserializationContext();
        if (deserializationContext != null) {
            logMessage.append("----- Deserialization Cache Info -----\n");
            logMessage.append("Cache size: ").append(deserializationContext.cachedDeserializersCount()).append("\n");
            logMessage.append("Cached deserializer types: \n");
            logMessage.append(getCachedDeserializerTypes(deserializationContext)).append("\n");
        }

        // Log the entire message as a single log statement
        logger.info(logMessage.toString());
    }

    /**
     * Uses reflection to get the cached serializer types from the DefaultSerializerProvider.
     */
    private static String getCachedSerializerTypes(DefaultSerializerProvider serializerProvider) {
        try {
            Field cacheField = DefaultSerializerProvider.class.getDeclaredField("_serializerCache");
            cacheField.setAccessible(true);
            Object cache = cacheField.get(serializerProvider);

            Field mapField = cache.getClass().getDeclaredField("_sharedMap");
            mapField.setAccessible(true);
            Map<?, ?> sharedMap = (Map<?, ?>) mapField.get(cache);

            StringBuilder cachedTypes = new StringBuilder();
            for (Object key : sharedMap.keySet()) {
                cachedTypes.append(key).append("\n");
            }

            return cachedTypes.toString();
        } catch (Exception e) {
            return "Unable to retrieve cached serializers.";
        }
    }

    /**
     * Uses reflection to get the cached deserializer types from the DefaultDeserializationContext.
     */
    private static String getCachedDeserializerTypes(DefaultDeserializationContext deserializationContext) {
        try {
            Field cacheField = DefaultDeserializationContext.class.getDeclaredField("_cache");
            cacheField.setAccessible(true);
            Object cache = cacheField.get(deserializationContext);

            Field mapField = cache.getClass().getDeclaredField("_sharedMap");
            mapField.setAccessible(true);
            Map<?, ?> sharedMap = (Map<?, ?>) mapField.get(cache);

            StringBuilder cachedTypes = new StringBuilder();
            for (Object key : sharedMap.keySet()) {
                cachedTypes.append(key).append("\n");
            }

            return cachedTypes.toString();
        } catch (Exception e) {
            return "Unable to retrieve cached deserializers.";
        }
    }
}
