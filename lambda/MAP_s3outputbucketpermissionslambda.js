const AWS = require('aws-sdk');
const util = require('util');

// Permissions for the new objects
// Key MUST match the top level folder
// Format: <owner account name> - <Canonical ID> - <sub account name> - <canonical ID>
// This will give owner full permission & sub account read only permission


// Main Loop
exports.handler = function(event, context, callback) {
    
    // If its an object delete, do nothing
    if (event.RequestType === 'Delete') {
    }
    else // Its an object put
    {
        // Get the source bucket from the S3 event
        var srcBucket = event.Records[0].s3.bucket.name;
        
        // Object key may have spaces or unicode non-ASCII characters, decode it
        var srcKey = decodeURIComponent(event.Records[0].s3.object.key.replace(/\+/g, " "));  

        // Gets the top level folder, which is the key for the permissions array        
        var folderID = srcKey.split("/")[0];

        var folderkey = process.env.outputfolder;
        var permissions = {
            folderkey: [process.env.payeraccountid, process.env.canonicalidpayer, process.env.linkedaccountid, process.env.canonicalidlinked]
        };

        // Define the object permissions, using the permissions array
        var params =
        {
            Bucket: srcBucket,
            Key: srcKey,
            AccessControlPolicy:
            {
                'Owner':
                {
                    'DisplayName': permissions[folderID][0],
                    'ID': permissions[folderID][1]
                },
                'Grants': 
                [
                    {
                        'Grantee': 
                        {
                            'Type': 'CanonicalUser',
                            'DisplayName': permissions[folderID][0],
                            'ID': permissions[folderID][1]
                        },
                        'Permission': 'FULL_CONTROL'
                    },
                    {
                        'Grantee': {
                            'Type': 'CanonicalUser',
                            'DisplayName': permissions[folderID][2],
                            'ID': permissions[folderID][3]
                            },
                        'Permission': 'READ'
                    },
                ]
            }
        };

        // get reference to S3 client 
        var s3 = new AWS.S3();

        // Put the ACL on the object
        s3.putObjectAcl(params, function(err, data) {
            if (err) console.log(err, err.stack); // an error occurred
            else     console.log(data);           // successful response
        });
    }
 };
