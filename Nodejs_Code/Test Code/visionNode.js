    // Imports the Google Cloud client library
    const vision = require('@google-cloud/vision');
  
    // Creates a client
    const client = new vision.ImageAnnotatorClient();
  
    // Performs label detection on the image file

    client
        .labelDetection('/Users/gabesaldivar/Desktop/vision_test/NodePics/pill.jpg')
        .then(results => {
            const labels = results[0].labelAnnotations;
            console.log('Labels:');
            labels.forEach(label => console.log(label.description));
        })
        .catch(err => {
            console.error('Error:', err);
        })
