const { CloudantV1 } = require('@ibm-cloud/cloudant');
const { IamAuthenticator } = require('ibm-cloud-sdk-core');
const md5 = require('spark-md5');

async function main(params) {
    const dbName = "reviews";
	const authenticator = new IamAuthenticator({ apikey: params.IAM_API_KEY })
    const cloudant = CloudantV1.newInstance({
      authenticator: authenticator
    });
    cloudant.setServiceUrl(params.COUCH_URL);
    
    let records;
    
    if(params.dealerId){
        records = await getMatchingRecords(cloudant,dbName,{dealership:params.dealerId});
        records = formatQueryResult(records);
    }else{
        records = await getAllRecords(cloudant,dbName);
        records = formatResult(records);
    }
    
    return records;
}


 function getAllRecords(cloudant,dbname) {
     return new Promise((resolve, reject) => {
         cloudant.postAllDocs({ db: dbname, includeDocs: true , limit: 10 })            
             .then((result)=>{
               resolve({result:result.result.rows});
             })
             .catch(err => {
                console.log(err);
                reject({ err: err });
             });
         })
 }
 
 function formatResult(params) {
  return {
    entries: params.result.map((row) => { return {
      id: row.doc.id,
      name: row.doc.name,
      dealership: row.doc.dealership,
      review: row.doc.review,
      purchase: row.doc.purchase,
      purchase_date: row.doc.purchase_date,
      car_make: row.doc.car_make,
      car_model: row.doc.car_model,
      car_year: row.doc.car_year
    }})
  };
}

 function formatQueryResult(params) {
     
  return {
    entries: params.result.map((row) => { return {
      id: row.id,
      name: row.name,
      dealership: row.dealership,
      review: row.review,
      purchase: row.purchase,
      purchase_date: row.purchase_date,
      car_make: row.car_make,
      car_model: row.car_model,
      car_year: row.car_year
    }})
  };
}

 /*
 Sample implementation to get the records in a db based on a selector. If selector is empty, it returns all records. 
 eg: selector = {state:"Texas"} - Will return all records which has value 'Texas' in the column 'State'
 */
 function getMatchingRecords(cloudant,dbname, selector) {
     return new Promise((resolve, reject) => {
         cloudant.postFind({db:dbname,selector:selector})
                 .then((result)=>{
                   resolve({result:result.result.docs});
                 })
                 .catch(err => {
                    console.log(err);
                     reject({ err: err });
                 });
          })
 }