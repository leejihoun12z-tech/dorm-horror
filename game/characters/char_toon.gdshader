shader_type spatial;
// 캐릭터 공용 툰 셰이더: 빛을 받는 툰(밤 손전등이 먹음) + 머리카락 끝 색 + 그린 얼굴(정면 평면 투영).
render_mode diffuse_toon, specular_toon;

uniform vec4 base_color : source_color = vec4(1.0);
uniform float roughness_value : hint_range(0.0, 1.0) = 0.6;
uniform float specular_value : hint_range(0.0, 1.0) = 0.5;
uniform bool use_tip = false;
uniform vec4 tip_color : source_color = vec4(0.8, 0.08, 0.14, 1.0);
uniform float tip_y = 0.0;
uniform float tip_soft = 0.012;
uniform bool use_face = false;
uniform sampler2D face_tex : source_color, filter_linear_mipmap;
uniform vec2 face_center = vec2(0.0, 0.0);
uniform vec2 face_size = vec2(0.26, 0.26);

varying vec3 local_pos;

void vertex() {
	local_pos = VERTEX;
}

void fragment() {
	vec3 col = base_color.rgb;
	if (use_tip) {
		float t = smoothstep(tip_y + tip_soft, tip_y - tip_soft, local_pos.y);
		col = mix(col, tip_color.rgb, t);
	}
	if (use_face && local_pos.z > 0.0) {
		vec2 uv = vec2((local_pos.x - face_center.x) / face_size.x + 0.5, 0.5 - (local_pos.y - face_center.y) / face_size.y);
		if (uv.x > 0.0 && uv.x < 1.0 && uv.y > 0.0 && uv.y < 1.0) {
			vec4 f = texture(face_tex, uv);
			col = mix(col, f.rgb, f.a);
		}
	}
	ALBEDO = col;
	ROUGHNESS = roughness_value;
	SPECULAR = specular_value;
}
