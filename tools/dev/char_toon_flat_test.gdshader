shader_type spatial;
// 캐릭터 공용 툰 셰이더: 빛을 받는 툰(밤 손전등이 먹음) + 머리카락 끝 색 + 그린 얼굴(정면 평면 투영).
// 시험용 복사본: 빛을 면 방향(법선)과 거의 상관없이 받음 → 울퉁불퉁한 면이 안 드러남. 손전등 거리·그림자는 그대로.
uniform float nl_amount : hint_range(0.0, 1.0) = 0.0;

uniform vec4 base_color : source_color = vec4(1.0);
uniform float roughness_value : hint_range(0.0, 1.0) = 0.6;
uniform float specular_value : hint_range(0.0, 1.0) = 0.5;
// 실제 부품(glb): 색을 면마다 칠한 정점 색으로 받음
uniform bool use_vcol = false;
// 실제 부품(Tripo): 색 = 구운 텍스처 한 장(UV)
uniform bool use_tex = false;
uniform sampler2D albedo_tex : source_color, filter_linear_mipmap;
uniform bool use_tip = false;
uniform vec4 tip_color : source_color = vec4(0.8, 0.08, 0.14, 1.0);
uniform float tip_y = 0.0;
uniform float tip_soft = 0.012;
uniform bool use_face = false;
uniform sampler2D face_tex : source_color, filter_linear_mipmap;
uniform vec2 face_center = vec2(0.0, 0.0);
uniform vec2 face_size = vec2(0.26, 0.26);

// 얼굴 그림은 정면 평면 투영 → 옆을 보는 면(볼 옆)에서는 그림이 늘어나므로 흐리게 뺀다
uniform float face_front_min = 0.35;
// 확인용: 0 = 보통 · 1 = 조명 없이 색만 · 2 = 색 없이 회색(모양·빛만)
uniform int debug_view = 0;
uniform float face_front_full = 0.6;

varying vec3 local_pos;
varying vec3 local_nrm;

void vertex() {
	local_pos = VERTEX;
	local_nrm = NORMAL;
}

void light() {
	float t = smoothstep(-0.3, 0.3, dot(NORMAL, LIGHT));
	DIFFUSE_LIGHT += mix(1.0, t, nl_amount) * ATTENUATION * LIGHT_COLOR / PI;
}

void fragment() {
	vec3 col = use_tex ? texture(albedo_tex, UV).rgb * base_color.rgb : (use_vcol ? COLOR.rgb * base_color.rgb : base_color.rgb);
	if (use_tip) {
		float t = smoothstep(tip_y + tip_soft, tip_y - tip_soft, local_pos.y);
		col = mix(col, tip_color.rgb, t);
	}
	if (use_face && local_pos.z > 0.0) {
		vec2 uv = vec2((local_pos.x - face_center.x) / face_size.x + 0.5, 0.5 - (local_pos.y - face_center.y) / face_size.y);
		if (uv.x > 0.0 && uv.x < 1.0 && uv.y > 0.0 && uv.y < 1.0) {
			vec4 f = texture(face_tex, uv);
			float front = smoothstep(face_front_min, face_front_full, normalize(local_nrm).z);
			col = mix(col, f.rgb, f.a * front);
		}
	}
	if (debug_view == 1) {
		EMISSION = col;
		col = vec3(0.0);
	} else if (debug_view == 2) {
		col = vec3(0.78);
	}
	ALBEDO = col;
	ROUGHNESS = roughness_value;
	SPECULAR = specular_value;
}
