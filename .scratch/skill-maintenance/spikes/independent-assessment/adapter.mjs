// Selected reference facets are evaluation units, not an accepted learning taxonomy.
export function packets(blind) {
 return blind.questions.flatMap(q=>q.responses.map(r=>({
  case_id:r.response_id,
  attempt:{id:r.response_id,origin:'recorded',phase:'current'},
  exercise:{prompt:q.question,reference:q.reference_answer,criteria:q.facets.map(f=>({id:f.id,rule:`Interpret ${f.govText} — ${f.reltn} — ${f.modText} in the complete reference answer; preserve its linked propositions.`,sourceFacet:f}))},
  response:r.response,
  context:[{id:'reference-context',role:'assessment_reference',text:q.reference_answer,facets:q.context_facets},
   {id:'conditions',role:'dataset_metadata',text:'Archived student response. Prior teaching, assistance, timing and learner history are unavailable. This is a selected-facet view, not a complete grade.'}],
  assistance:[],source:{question_id:q.question_id,module:q.module,path:q.source_path}
 })));
}
