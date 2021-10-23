//import org.json.JSONArray;
//import org.json.JSONException;
import org.codehaus.jettison.json.JSONArray;
import org.codehaus.jettison.json.JSONException;
import org.codehaus.jettison.json.JSONObject;
import java.io.FileWriter;
import java.io.IOException;
import java.util.*;

public class JSONConverter {
    private final static String json = "{\"full\":{   \"id\":1,\n" +
            "    \"name\":\"abc\",\n" +
            "    \"address\": {\"streetName\":\"cde\",\n" +
            "                \"streetId\":2.2\n" +
            "                },\n" +
            "    \"config\":[\n" +
            "        {\"param1\":\"obj1\",\n" +
            "        \"param2\":\"obj2\"}\n" +
            "    ]\n" +
            "\n" +
            "}\n" +
            "}\n";

    private String getType(Object value){
        if(value.getClass()==String.class){
            return "textValues";
        }
        else if(value.getClass()==Integer.class){
            return "integerValues";
        }
        else if(value.getClass()==Double.class){
            return "floatValues";
        }
        return "propertyValues";
    }

    private JSONObject propertyValues(String name, Object values) throws JSONException {
        JSONObject jsonObject = new JSONObject();
        String valuetype = getType(values);
        jsonObject.put("name", name);
        if (valuetype.equals("propertyValues")) {
            jsonObject.put(valuetype, values);
        }else{
            jsonObject.put(valuetype, new JSONObject().put("values", new JSONArray().put(values)));
        }
        return jsonObject;
    }

    private JSONObject parseJSONObjectToMap(JSONObject jsonObject) throws JSONException{
        JSONObject mapData =  new JSONObject();
        Iterator<String> keysItr = jsonObject.keys();
        JSONArray jsonArray = new JSONArray();
        while(keysItr.hasNext()) {
            String key = keysItr.next();
            Object value = jsonObject.get(key);
            if(value instanceof JSONArray) {
                value = parseJSONArrayToList((JSONArray) value);
            }else if(value instanceof JSONObject) {
                value = parseJSONObjectToMap((JSONObject) value);
            }
            JSONObject formattedJson = propertyValues(key,value);
            jsonArray.put(formattedJson);
        }
        mapData.put("properties", jsonArray);
        return mapData;
    }

    private JSONArray parseJSONArrayToList(JSONArray array) throws JSONException {
        JSONArray list = new JSONArray();
        for(int i = 0; i < array.length(); i++) {
            Object value = array.get(i);
            if(value instanceof JSONArray) {
                value = parseJSONArrayToList((JSONArray) value);
            }else if(value instanceof JSONObject) {
                value = parseJSONObjectToMap((JSONObject) value);
            }
            list.put(value);
        }
        return list;
    }
    public JSONObject convert(String json){
        try {
            JSONObject jsonObject = new JSONObject(json);
            JSONObject transformedJSON = parseJSONObjectToMap(jsonObject);
            return transformedJSON;
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return null;
    }
    public static void main(String[] args) throws JSONException {
        JSONConverter jsonConverter = new JSONConverter();
        JSONObject check = jsonConverter.convert(json);
        System.out.println("-------------------------");
        System.out.println(check.toString(4));
        FileWriter file = null;
        try {
            file = new FileWriter("./check.json");
            file.write(check.toString(4));
            file.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
