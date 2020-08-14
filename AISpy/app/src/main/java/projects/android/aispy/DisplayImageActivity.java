package projects.android.aispy;

import android.annotation.SuppressLint;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.text.method.ScrollingMovementMethod;
import android.view.View;
import android.widget.ImageView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.api.services.vision.v1.model.Feature;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;

/**
 * DisplayImageActivity is called as an Intent immediately after a user successfully takes a picture. In this activity,
 * the an AISpyImage singleton object is created as a representation of the image including all relevant meta-data. After
 * the AISpyImage is created, the user can navigate to the WelcomeActivity Intent and play a game of AISpy
 */
public class DisplayImageActivity extends AppCompatActivity {
    private ImageView imageView;
    private Bitmap bitmap;
    private Feature feature;
    private Spinner spinnerVisionAPI;
    private TextView allLabelsView;


    private String[] visionAPI = new String[]{"LABEL_DETECTION","LANDMARK_DETECTION", "LOGO_DETECTION", "SAFE_SEARCH_DETECTION", "IMAGE_PROPERTIES"};
    private String api = visionAPI[0];

    private final String BAD_PHOTO_PROMPT = "There's not a lot going on in this photo. Please choose another one";
    private final String NOT_READY_PROMPT = "AI Spy is not ready";

    private String imagePath;
    private AISpyImage aiSpyImage;



    @Override
    protected void onCreate(Bundle savedInstanceState){
        super.onCreate(savedInstanceState);
        setContentView(R.layout.display_image_layout);
        imageView = findViewById(R.id.imageView);
        imagePath = getIntent().getStringExtra("image_path");

        Bitmap picture = BitmapAPI.getCorrectOrientation(imagePath);
        imageView.setImageBitmap(picture);

        allLabelsView = findViewById(R.id.allLabels);
        allLabelsView.setText("Processing...");

        Context thisContent = this.getApplicationContext();


        //Asynchronously creates the AISpyImage representation
//        new AsyncTask<Object, Void, ArrayList<AISpyObject>>() {
        new AsyncTask<Object, Void, AISpyImage>() {
            @SuppressLint("StaticFieldLeak")
            @Override
            protected AISpyImage doInBackground(Object... params) { //TODO: Once all apis are implemented, this should return the full image data structure that we want to build (A map of colors to objects)

                try {
                    AISpyImage.setInstance(thisContent, getExternalFilesDir(Environment.DIRECTORY_PICTURES), imagePath);
                    AISpyImage aiSpyImage = AISpyImage.getInstance();
                    return aiSpyImage;
                } catch (IOException e) {
                    e.printStackTrace();
                }
                return null;
            }

            protected void onPostExecute(AISpyImage generatedAiSpyImage) {
                displayAISpyObjects(generatedAiSpyImage);

                aiSpyImage = generatedAiSpyImage;

                handleBadImage(thisContent);
            }
        }.execute();

    }

    /**
     * Creates a readable representation of all detected AISpyObjects and displays it to the screen
     * @param generatedAiSpyImage
     */
    private void displayAISpyObjects(AISpyImage generatedAiSpyImage){
        String allLabelsText = generatedAiSpyImage.getAllLabelsText();
        allLabelsView.setText(allLabelsText);

        ImageView[] objectImages = {findViewById(R.id.objectView1), findViewById(R.id.objectView2), findViewById(R.id.objectView3), findViewById(R.id.objectView4), findViewById(R.id.objectView5), findViewById(R.id.objectView6)};
        TextView[] objectText = {findViewById(R.id.objectText1), findViewById(R.id.objectText2), findViewById(R.id.objectText3), findViewById(R.id.objectText4), findViewById(R.id.objectText5), findViewById(R.id.objectText6)};

        ArrayList<AISpyObject> allObjects = generatedAiSpyImage.getAllObjects();
        HashMap<AISpyObject, Features> iSpyMap = generatedAiSpyImage.getiSpyMap();
        for (int i = 0; i < allObjects.size() && i < objectImages.length; i++){
            AISpyObject object = allObjects.get(i);
            objectImages[i].setImageBitmap(allObjects.get(i).getImage());
            String wiki = iSpyMap.get(object).wiki;
            if ( wiki == null) wiki = "";
            objectText[i].setMovementMethod(new ScrollingMovementMethod());
            HashMap<String, ArrayList<String>> conceptNetMap = iSpyMap.get(object).conceptNet;
            objectText[i].setText("Labels:" + "\n" + object.getLabelsText() + "\n\n" + "Color: " + object.getColor() + "\n\n" + "Wiki:" + wiki+ "\n\n" + ConceptNetAPI.getReadableRepresentation(conceptNetMap));
        }
    }

    /**
     * Starts the WelcomeActivity Intent
     * @param view
     */
    public void playAISpy(View view) {
        if (aiSpyImage != null) {
            Intent intent = new Intent(this, WelcomeActivity.class);
            startActivity(intent);
        } else {
            Toast toast= Toast.makeText(getApplicationContext(),NOT_READY_PROMPT, Toast.LENGTH_SHORT);
            toast.show();
        }
    }

    /**
     * If no objects were detected in the image, prompts the user to try choosing another photo and takes user back to MainActivity
     */
    private void handleBadImage(Context thisContent){
        if (aiSpyImage.getAllObjects().size() == 0){
            Toast toast= Toast.makeText(getApplicationContext(),BAD_PHOTO_PROMPT, Toast.LENGTH_SHORT);
            toast.show();

            Intent intent = new Intent(thisContent, MainActivity.class);
            startActivity(intent);
        }
    }
}
